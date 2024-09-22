def model_moving_average(df):
    df = df.sort_values('timestamp')
    df['bollinger_middle'] = df['close'].rolling(window=20).mean()
    df['bollinger_std'] = df['close'].rolling(window=20).std()
    df['bollinger_upper'] = df['bollinger_middle'] + (df['bollinger_std'] * 2)
    df['bollinger_lower'] = df['bollinger_middle'] - (df['bollinger_std'] * 2)
    
    df['buy_signal'] = (df['close'] < df['bollinger_lower'])
    df['sell_signal'] = (df['close'] > df['bollinger_upper'])
    
    return df
