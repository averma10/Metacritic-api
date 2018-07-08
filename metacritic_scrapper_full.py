import metacritic_api_full
import os,sys,json
from string import lowercase

#RANGE = lowercase
RANGE = 'a'
#publications_by = ['name','score','popular',]
publications_by = 'name'

def save_file(obj,file_name):
    with open(file_name,'w') as outfile:
        json.dump(obj,outfile)

#create a new directory to store data
if not os.path.exists('data'):
    os.makedirs('data')


#save publication names
all_publications = []
for category in ['movies','games','tv','music']:
    if publications_by == 'name':
        for letter in str(RANGE):
            publications = get_publication_names(letter,category=category,select_by = publications_by)
            if publications != None:
                all_publications+=publications
        #print all_publications
    else:
        publications = get_publication_names(category=category,select_by = publications_by)
        all_publications = publications
if publications_by =='name':
    save_file(all_publications,'data/publication_names_{}-{}.json'.format(str(RANGE[0]),str(RANGE[-1])))
    #print all_publications
else:
    save_file(all_publications,'data/publication_names_by_{}.json'.format(publications_by))
    

#save reviews for all the publications
reviews = []
for publication in all_publications:
    reviews.append(metacritic_api_full.get_all_critic_reviews(publication_name = publication['publication_name'],category = publication['category']))
    #print 'publication name: {}\t\tcategory: {}'.format(publication['publication_name'],publication['category'])
if publications_by =='name':
    save_file(reviews,'data/critic_reviews_{}-{}.json'.format(str(RANGE[0]),str(RANGE[-1])))
else:
    save_file(reviews,'data/critic_reviews_by_{}.json'.format(publications_by))

