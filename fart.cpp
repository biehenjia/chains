
struct WORD {
    char word[20];
    int count;
};

struct WORDSTATS {
    int line_count;
    int word_count;
    int keyword_count; 
};

int populate_dictionary(FILE *fp, char *dictionary);


bool contain_word(char *dictionary, char *word){

}