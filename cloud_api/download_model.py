from huggingface_hub import snapshot_download

print("Downloading CLAP...")
snapshot_download(repo_id="laion/clap-htsat-unfused", local_dir="./model_cache")
print("Done")