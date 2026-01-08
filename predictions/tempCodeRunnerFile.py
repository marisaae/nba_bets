predictions = predict_next_game(prediction_df, STAT_CONFIGS)
print(tabulate(predictions, headers="keys", tablefmt="fancy_grid"))