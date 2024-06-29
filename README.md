# Video Games Recommendation System Using K-Means Clustering
### By Alex D. Lopez for Ironhack DA spring-2024 bootcamp for the Final Project

For my final project in my Data Analytics Bootcamp, I made a recommendation system 
for video Games using K-Means Clustering, utilizing the implementation from the scikit-learn 
python library.     

## Requirements :
- Python 3.10+ (Used Google colab for Notebooks)
- Numpy
- Pandas
- Matplotlib
- Seaborn
- scikit-learn

## Project Structure:
- Jupyter Notebooks: Split the code for Cleaning, Modeling K-Means, 
  and implementation of Recommendation Model.
- Data Folders: 
	- The initial unfiltered data is in original scraped data folder, with the full merged csv and the original component files. 
	  the component files were merged into the full csv file using pd.merge using the rank column as the joining column
	- Cleaned Data folder contained the cleaned data generated from the Cleaning Notebook
	- Recommendation Data Folder contains the transformed data generated from the Data Modeling Notebook
- Presentation: Contains the powerpoint slides for my project. The link to the original in Google Slides is also available down below in the Presentation section.
- Platform Abbrev. Folder: Misc. folder that contains a document file containing what the Abbreviated platform data in the dataset 
						   are actually referring to. It Is very useful for the more obscure game consoles/platforms.
	
## Dataset Source
Found data from [Video Games Sales Kaggle dataset](https://www.kaggle.com/datasets/gregorut/videogamesales/data),
which was scraped from [VGChartz](https://www.vgchartz.com/) 

I decided to use the scraper provided by the Kaggle dataset author [gregorut](https://github.com/GregorUT/) 
and rewrote part of it to handle read/rate limiting errors during the process.
 
I made 2 seperate scrapers because at some point, I wanted to get the user/critic scores from 
vg chartz for the Recommendation System. 

## Data Preparation:
### Cleaning 
The Video_Games_Clean.ipynb contains the following cleaning steps
- Nulls:
	- Drop nulls in Years, Publisher (Unknown -> NaN)
	- Filled nulls in Sales (NA, EU, JP, Other), Critic_Score, and User Score with 0.0
- invalid data; 
	- erroneous data for 5 game entries in Years column: dropped them
- Filtered out Platforms and Genres that barely show up in the data (min_threshold = 20)

### Feature Engineering
The Video_Games_Data_Modeling.ipynb contains these data manipulation/feature Engineering steps
- Binning
	- Binned Publishers into 3 categories: Low. Medium, High Profile
	
- Aggregated Game entries 
	- Summed sales data
	- Averaged out Critic/User Scores (ignoring no scores)
    - Concatenated release Platforms
	
- Encoding:
	- Label Encode the Binned Publishers (low-high -> 0-2)
	- One Hot Encode Genre
	
- Scaling: 
	- Scaled data for Sales columns & Critic Score/User Scores
	- Experimented with 3 scalers: ultimately settled on Min Max Scaler

## Machine Learning
**K-Means Clustering** 

Graphed the optimal K  using Elbow method and Silhoutte Score.
 
Tested and Tuning for 2 factors:
- scalers (Min-Max, Standard, Robust)
- Data : Full dataset, dropping the sales, dropping the scores, & dropping both. 

For the model, I choses to drop the critic and user scores of the transformed data, and 
used Min-Max Scaler. Optimal K was 43 clusters

Cluster predictions were put into the transformed dataframe and stored in a csv file for the 
Recommendation Notebook

Results of the clustering are investigated at the end of the Notebook:

The clusters group the data mainly by combination of a publisher profile type and a Genre.

A couple of clusters had either Publisher profile types and/or 2 genres associated.  

## Recommendation Model
the Video_Game_Recommendations.ipynb does the following:
- Look up the game inputted in the K-Means transformed Video Game csv file
	- If it finds nothing; asks for reprompt
	- If multiple entries were matched, prompt user to pick a specific one (1 - N)
- Find and return all the games in the same cluster as the inputted game
- Return recommendations by sorting cluster group by Critic_Score, User_Score, Rank (Descending for scores, Ascending for Rank)
	- Number of returned games is specified in "Pages" where each page represents 10 results
	- User can choose how many pages of results to return

### Presentation
You may access my presentation on Google slides [here](https://docs.google.com/presentation/d/14vXupVNBGev8nIVDhgMaeiqikF21kQjbruuglJKCcpU/edit?usp=sharing)

If the link doesn't work, you should be able to access it by downloading the .ppt file in the Presentation folder
