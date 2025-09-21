from modules.provenance.provenance_logic import provenance_pipeline

if __name__ == "__main__":
    result = provenance_pipeline("NASA confirmed Earth will go dark for 6 days", media_file=None)
    print(result)
