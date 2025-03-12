import pandas as pd
from bing_image_downloader import downloader

df = pd.read_parquet("logos.snappy.parquet")
#print(type(df)) ran this to see if its dataframe or series (its dataframe)
x = 0
for value in df.iloc[:, 0]:  # Selecting the first column
	downloader.download(value + " logo", limit = 2, output_dir = '.',
                    adult_filter_off = True, force_replace = False, timeout = 60)
	x += 1
	if x == 10:
		break