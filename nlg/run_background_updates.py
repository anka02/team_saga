from create_summarization_dict import create_dict_for_summarization,write_dictionary,DICT_FOR_SUMM_PATH #search_info,
from generate_summarization_in_dict import do_summarization_in_dict,DICT_SUM_PATH, write_in_dict
import time

def update_dictionary():
    dictionary_for_summarization = create_dict_for_summarization()
    #print("Dictionary for summarization has been created")
    write_dictionary(dictionary_for_summarization )  # not necessairy could be removed
    # print("Dictionary for summarization has been written")
    # print("Waiting for summarization process.")
    dictionary_summarized = do_summarization_in_dict(dictionary_for_summarization)
    #print("Dictionary with summarized texted has been created")
    write_in_dict(dictionary_summarized)
    # print("Dictionary with summarized texted has been written")
    # print("The action Server is running. Chat-bot is ready to use")


if __name__ == '__main__':
    print("Update starting ...")
    while True:
        print("Next update waiting")
        time.sleep(7200)
        update_dictionary()
