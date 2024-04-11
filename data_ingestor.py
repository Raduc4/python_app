import pandas as pd
import json

class DataIngestor:
    def __init__(self, csv_path: str):
        self.data = pd.read_csv(csv_path)

        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic physical activity and engage in muscle-strengthening activities on 2 or more days a week',
            'Percent of adults who achieve at least 300 minutes a week of moderate-intensity aerobic physical activity or 150 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week',
        ]

    def average(self, question: str, state: str | None = None, global_avg: bool = False):
        if global_avg:
            df = self.data[self.data['Question'] == question]['Data_Value'].mean()
            return {'global_mean': df}
        
        df = self.data[self.data['Question'] == question].groupby('LocationDesc')['Data_Value'].mean().sort_values(ascending=True)
        if state:
            return {state: df[state]}
        return json.loads(df.to_json(orient='index'))
    
    def top5(self, question: str, type: str):
        if type == "best":
            if question in self.questions_best_is_min:
                df = self.data[self.data['Question'] == question].groupby('LocationDesc')['Data_Value'].mean().sort_values(ascending=True).head(5)
            else:
                df = self.data[self.data['Question'] == question].groupby('LocationDesc')['Data_Value'].mean().sort_values(ascending=False).head(5)
        else:
            if question in self.questions_best_is_min:
                df = self.data[self.data['Question'] == question].groupby('LocationDesc')['Data_Value'].mean().sort_values(ascending=False).head(5)
            else:
                df = self.data[self.data['Question'] == question].groupby('LocationDesc')['Data_Value'].mean().sort_values(ascending=True).head(5)
        
        return json.loads(df.to_json(orient='index'))
    
    def diff_from_average(self, question: str, state: str | None = None):
        global_avg = self.data[self.data['Question'] == question]['Data_Value'].mean()
        if state:
            df = global_avg - self.data[(self.data['Question'] == question) & (self.data['LocationDesc'] == state)]['Data_Value'].mean()
            return {state: df}
        
        df = global_avg - self.data[self.data['Question'] == question].groupby('LocationDesc')['Data_Value'].mean()
        return json.loads(df.to_json(orient='index'))
    
    def average_by_category(self, question: str, state: str | None = None):
        if state:
            df = self.data[(self.data['Question'] == question) & (self.data['LocationDesc'] == state)].groupby(['StratificationCategory1', 'Stratification1'])['Data_Value'].mean()
            return {state: json.loads(df.to_json(orient='index'))}
        
        df = self.data[self.data['Question'] == question].groupby(['LocationDesc', 'StratificationCategory1', 'Stratification1'])['Data_Value'].mean()
        return json.loads(df.to_json(orient='index'))