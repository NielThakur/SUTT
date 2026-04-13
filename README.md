Task Pipeline -
|_Enter Query.
|_Based on entered query, stories are fetched from API.
|_Each story data is recorded and displayed.
|_For each story the comment data is fetched using API based on ID.This happens recursively and based on depth to identify the nested replies.
|_Data is sorted into chunks based on depth defined earlier.
|_Chunks are then put into summarize function that gives out a summary.
