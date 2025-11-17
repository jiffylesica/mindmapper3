from mindmapper.pipeline import TextToGraphPipeline 
from dotenv import load_dotenv

load_dotenv()
pipeline = TextToGraphPipeline("document_data/raw_txt/test.txt")
pipeline.run_pipeline(4, 3)