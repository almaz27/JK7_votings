import pandas as pd

def arrange_votings(fname):
    # convert csv to dataframe for arrange
    data = pd.read_csv(fname)
    # collect Deputy names
    vote = pd.concat([data['Депутаты'], data['Депутаты.1'], data['Депутаты.2']], ignore_index=True) \
    .dropna().to_frame().rename(columns={0:'Депутаты'})
    # collect votes
    vote['Результат'] = pd.concat([data['Результат'], data['Результат.1'],data['Результат.2']], ignore_index=True) \
    .dropna().to_list()
    # print(vote.head())
    return vote













