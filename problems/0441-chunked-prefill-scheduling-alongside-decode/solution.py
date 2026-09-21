def chunked_prefill_schedule(
    prefill_requests,
    decode_requests,
    max_batch_tokens,
    max_chunk_size
):
    prefill_queue = [
        {
            "id": r["id"],
            "remaining_prompt": r["prompt_tokens"],
            "decode_tokens": r["decode_tokens"]
        }
        for r in prefill_requests
    ]

    decode_pool = [
        {
            "id": r["id"],
            "remaining_decode": r["remaining_decode"]
        }
        for r in decode_requests
    ]

    schedule = []
    step = 0

    while prefill_queue or decode_pool:

        # 1. Decode first
        decode_ids = []

        for req in decode_pool:
            if req["remaining_decode"] > 0:
                decode_ids.append(req["id"])
                req["remaining_decode"] -= 1

        used_tokens = len(decode_ids)

        # 2. Remaining budget is available for prefill
        remaining_budget = max_batch_tokens - used_tokens

        prefill_chunks = []

        # Process each prefill request at most once this step
        queue_length = len(prefill_queue)

        for _ in range(queue_length):

            if remaining_budget <= 0:
                break

            req = prefill_queue.pop(0)

            chunk_size = min(
                req["remaining_prompt"],
                max_chunk_size,
                remaining_budget
            )

            prefill_chunks.append(
                (req["id"], chunk_size)
            )

            req["remaining_prompt"] -= chunk_size
            remaining_budget -= chunk_size

            # If prefill is not finished, put it back at the end
            if req["remaining_prompt"] > 0:
                prefill_queue.append(req)

            # If finished, add to decode pool
            else:
                if req["decode_tokens"] > 0:
                    decode_pool.append({
                        "id": req["id"],
                        "remaining_decode": req["decode_tokens"]
                    })

        # 3. Remove exhausted decode requests
        decode_pool = [
            req for req in decode_pool
            if req["remaining_decode"] > 0
        ]

        total_tokens = used_tokens + sum(
            size for _, size in prefill_chunks
        )

        schedule.append({
            "step": step,
            "prefill_chunks": prefill_chunks,
            "decode_ids": decode_ids,
            "total_tokens": total_tokens
        })

        step += 1

    return schedule