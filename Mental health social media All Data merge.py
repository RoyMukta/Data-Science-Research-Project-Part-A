import pandas as pd
import glob

# Gather all the individual post CSVs
post_files = glob.glob("beyondblue_*_posts_full.csv")

# Also include the depression file
post_files.append("beyondblue_depression_posts_all.csv")

print(f"Files to merge ({len(post_files)}):")
for f in post_files:
    print(" -", f)

# Read and concatenate without dropping any records
df_list = [pd.read_csv(f) for f in post_files]
merged_df = pd.concat(df_list, ignore_index=True)

# Save to requested output filename
output_file = "Mental health social media data.csv"
merged_df.to_csv(output_file, index=False, encoding="utf-8")
print(f"Merged {len(merged_df)} records into '{output_file}'")
