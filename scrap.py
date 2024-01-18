from langchain.document_loaders import AsyncChromiumLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_transformers import Html2TextTransformer
from langchain.chains import create_extraction_chain
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser
import dotenv
import json
import pprint
dotenv.load_dotenv()

# "gpt-3.5-turbo-1106")


# schema = Object(
#     id="Places Data",
#     description="Schema to extract data",
#     attributes=[
#         Text(id="type", description="Type of property for sale", examples=[("Spacious One Kanal House For Sale In DHA Phase 2, Islamabad", "House"), ("Plot For Sale Sector N Clear Land Possession Within 6 Month Solid Land At Prime Location Bahria Enclave Islamabad", "Plot")]),
#         Text(id="price", description="Price of property for sale", examples=[("PKR 4.8 Crore\nBahria Enclave, Bahria Town", "4.8 Crore"), ("Starting from PKR 34.65 Lakh", "34.65 Lakh"), ("PKR 90 Thousand \nDHA phase 2 - Sector J", "90 Thousand")]),
#         Text(id="location", description="Location of property", examples=[("PKR 4.8 Crore\nBahria Enclave, Bahria Town", "Bahria Enclave, Bahria Town"), ]),
#         Text(id="baths", description="Baths in house", examples=[("PKR 4.8 Crore 5 4 10 Marla", "4"), ("Titanium PKR 8 Crore 5 6 1 Kanal Brand New House For Sale In B-17", "6")]),
#         Text(id="area", description="Area of property", examples=[("PKR 4.8 Crore 5 4 10 Marla", "10 Marla"), ("Titanium PKR 8 Crore 5 6 1 Kanal Brand New House For Sale In B-17", "1 Kanal")]),
#         Text(id="bedrooms", description="Bedrooms in house", examples=[("PKR 4.8 Crore 5 4 10 Marla", "5"), ("Titanium PKR 8 Crore 5 6 1 Kanal Brand New House For Sale In B-17", "5")]),
#         Text(id="purpose", description="Purpose of advertisement", examples=[("Titanium PKR 8 Crore 5 6 1 Kanal Brand New House For Sale In B-17", "Sale")])
#     ],
#     many=True
# )


schema = {
    "properties": {
        "type_of_property": {"type": "string"},
        "price_of_property_listing": {"type": "string"},
        "location_of_property_listed": {"type": "string"},

        "area_of_property_listed": {"type": "string"},
        "purpose_of_listing": {"type": "string"}

    },
    "required": ["type_of_property", "price_of_property_listing", "location_of_property_listed", "area_of_property_listed", "purpose_of_listing"]
}


def scrape_with_playwright(urls, schema, api_key):
    print("urls => ", urls, " schema => ", schema, " api_key => ", api_key)
    llm = ChatOpenAI(temperature=0, model="gpt-4", api_key=api_key)

    def extract(content: str, schema: dict):
        return create_extraction_chain(schema=schema, llm=llm).run(content)

    loader = AsyncChromiumLoader(urls)
    docs = loader.load()
    bs_transformer = Html2TextTransformer()
    docs_transformed = bs_transformer.transform_documents(
        docs, tags_to_extract=["span"]
    )
    print("Extracting content with LLM")

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    splits = splitter.split_documents(docs_transformed)
    scraped_data = []
    for split in splits:
        scraped_data.append(extract(
            schema=schema, content=split.page_content))
        # # pprint.pprint(extracted_content)
        # json.dump(extracted_content, file, indent=2)
    return scraped_data


# urls = ["https://www.zameen.com/Homes/Islamabad-3-1.html"]
# scrape_with_playwright(urls, schema=schema)
