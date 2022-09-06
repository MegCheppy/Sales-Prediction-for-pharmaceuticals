import numpy as np
import pandas as pd
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from functools import reduce
import os,sys
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.pipeline import Pipeline
from logger import logger


class Clean:
    """
    - this class is responsible for performing 
    Cleaning Tasks
    """

    def __init__(self, df):
        """initialize the cleaning class"""
        self.df = df
        logger.info("Successfully initialized clean class")

    def has_missing_values(self):
        """
        expects:
            -   nothing
        returns:
            -   boolean
        """
        has_missing_values = False
        if True in self.df.isnull().any().to_list():
            has_missing_values = True
        counts = None
        counts = self.df.isnull().sum()
        logger.info("Successfully checked for missing values")
        return counts,has_missing_values

    def store_features(self,type_,value):
        """
        purpose:
            - stores features for the data set
        input:
            - string,int,dataframe
        returns:
            - dataframe
        """
        features = [None]
        if type_ == "numeric":
            features = self.df.select_dtypes(include=value).columns.tolist()
        elif type_ == "categorical":
            features = self.df.select_dtypes(exclude=value).columns.tolist()
        logger.info("Successfully stored the features")
        return features

    def merge_df(self,df_,column):
        """
        expects:
            - string(column)
        returns:
            - merged df
        """
        try:
            column = column
        except Exception as e:
            logger.error(f'please add {e}')
        self.df = pd.merge(self.df, df_, how = 'left', on = column)
        logger.info("Successfully merged the dataframe")
        return self.df

    
    def handle_missing_values_numeric(self, features, df=None):
        """
        this algorithm does the following
        - remove columns with x percentage of missing values
        - fill the missing values with the mean
        returns:
            - df
            - percentage of missing values
        """
        if df:
            self.df=df
        missing_percentage = round((self.df.isnull().sum().sum()/\
                reduce(lambda x, y: x*y, self.df.shape))*100,2)
        for key in features:
            self.df[key] = self.df[key].fillna(self.df[key].mean())
        logger.info("Successfully handled missing values for numerical case")
        return missing_percentage, self.df

    def handle_missing_values_categorical(self,features):
        """
        this algorithm does the following
        - remove columns with x percentage of missing values
        - fill the missing values with the mode
        returns:
            - df
            - percentage of missing values
        """
        missing_percentage = round((self.df.isnull().sum().sum()/\
                reduce(lambda x, y: x*y, self.df.shape))*100,2)
        for key in features:
            self.df[key] = self.df[key].fillna(self.df[key].mode()[0])
        logger.info("Successfully handled missing values for categorical values")            
        return missing_percentage, self.df


    def drop_missing_values(self)->pd.DataFrame:
        """
        remove rows that has column names. This error originated from
        the data collection stage.  
        """
        self.df.dropna(inplace=True)
        logger.info("Successfully dropped the columns with missing values")
    
    def drop_duplicate(self, df:pd.DataFrame,column)->pd.DataFrame:
        """
        - this function drop duplicate rows
        """
        self.df = self.df.drop_duplicates(subset=[column])
        logger.info("Successfully dropped rows with duplicate values")
        return self.df
        
    def convert_to_datetime(self, column)->pd.DataFrame:
        """
        convert column to datetime
        """
        self.df[column] = pd.to_datetime(self.df[column])
        logger.info("Successfully converted the column to datetime")
        return self.df



    def fix_outliers(self,column,threshold):
        """
        - this algorithm fixes outliers
        """
        numerical_columns=self.store_features("numeric","number")
        for i in numerical_columns:
            if i == column:
                self.df = self.df[self.df[column] < threshold]  #Drops samples which have sales more than 25000
                self.df.reset_index(drop=True)
        logger.info("Successfully handled outliers")
        return

    def generate_pipeline(self,type_="numeric",x=1):
        """
        purpose:
            - generate_pipelines for the data
        input:
            - string and int
        returns:
            - pipeline
        """
        pipeline = None
        if type_ == "numeric":
            pipeline = Pipeline(steps=[
                ('impute', SimpleImputer(strategy='mean')),
                ('scale', MinMaxScaler())
            ])
        elif type_ == "categorical":
            pipeline = Pipeline(steps=[
            ('impute', SimpleImputer(strategy='most_frequent')),
            ('one-hot', OneHotEncoder(handle_unknown='ignore', sparse=False))
            ])
        else:
            pipeline = np.zeros(x)
        return pipeline
    
    def generate_transformation(self,df,type_,value,trim=None,key=None):
        """
        purpose:
            - generates transformations for the data
        input:
            - string,int and df
        returns:
            - transformation
        """
        transformation = None
        pipeline = self.generate_pipeline(type_,value)
        if type_=="numeric":
            transformation=pipeline.fit_transform(df.select_dtypes(include=value))
            logger.info("Successfully transformed numerical data")
        elif type_ == "categorical":
            transformation=pipeline.fit_transform(df.select_dtypes(exclude=value))
            logger.info("Successfully transformed categorical data")
        return transformation

    

    def remove_unnamed_cols(self):
        """
        - this algorithm removes columns with unnamed
        """
        self.df.drop(self.df.columns[self.df.columns.str.contains('unnamed',
        case = False)],axis = 1, inplace = True)
        logger.info("Successfully removed columns with head unnamed")
    
    def label_encoding(self,train,test):
        """
        - label encode the data
        """
        categorical_features=self.store_features("categorical","number")
        for dataset in (train,test):
            for f in categorical_features:
                dataset[categorical_features] = dataset[categorical_features].apply(lambda x: pd.factorize(x)[0])
        logger.info("Successfully encoded your categorical data")


    def transfrom_time_series(self,column,date_column):
        """
        - transform the data into a 
        time series dataset
        """
        self.df.sort_values([column,date_column], ignore_index=True, inplace=True)    
        self.df[date_column] = pd.to_datetime(self.df[date_column],errors='coerce')
        self.df['Day'] = self.df[date_column].dt.day
        self.df['Month'] = self.df[date_column].dt.month
        self.df['Year'] = self.df[date_column].dt.year
        self.df['DayOfYear'] = self.df[date_column].dt.dayofyear
        self.df['WeekOfYear'] = self.df[date_column].dt.weekofyear
        self.df.set_index(date_column, inplace=True)
        logger.info("Successfully transformed data to time series data")

    def save(self,name):
        """
        - returns the dataframes
        """
        self.df.to_csv(name,index=False)
        logger.info("Successfully saved the dataframe")

    def get_df(self):
        """
        - returns the dataframe
        """
        return self.df


    def aggregations(self,df,column=None,second_column=None,
                    third_column=None,according_to="sum"):
        """
        - this is for adding features based on aggregations
        """
        if according_to=="sum":
            grouped_x =  df.groupby([df[column]])[second_column].sum()
        elif according_to=="mean":
            grouped_x =  df.groupby([df[column]])[second_column].mean()
        grouped_y = df.groupby([df[column]])[third_column].count()
        per_x = grouped_x / grouped_y
        logger.info("successful aggregation")
        return dict(per_x)

##