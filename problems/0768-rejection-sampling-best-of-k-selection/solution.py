def rejection_sampling_best_of_k(candidates, scores):
    result = []

    for i in range(len(candidates)):
        best_index = 0

        for j in range(1, len(candidates[i])):
            if scores[i][j] > scores[i][best_index]:
                best_index = j

        result.append(candidates[i][best_index])

    return result