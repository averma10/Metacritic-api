import sys, urllib2, time, re, requests
from string import lowercase as lowercase_letters
from bs4 import BeautifulSoup


def get_url(letter = None,publication_name = 'name',filter_by = 'movies',num_items = 100, sort_option = 'critic_score',page_num = 0,publication_sort_by = 'name'):
    """
    This function generates a url based on the arguments provided.
    Args:
        letter: a single character or any number
        publication_name: a character/string
        filter_by: one of ['movies','games','tv','music']
        num_items: one of [30,100]
        sort_options: one of ['critic_score','date','metascore']
        page_num: a valid integer for pagination
        publication_sort_by: one of ['name','popular','score']
    Returns: metacritic page url
    """
    filter_dict = {
            'movies': 'movies',
            'games': 'games',
            'tv': 'tv',
            'music':'albums'
        }
    filter = filter_dict[str.lower(filter_by)]
    if letter !=None:
        if letter == '-1':
            raise Exception('Invalid letter selection. Please select a valid letter.')
        try: #proceed if letter is non-numeric
            letter = str.lower(letter)
            url = 'http://www.metacritic.com/browse/{0}/publication/name/{1}?num_items={2}'.format(filter,letter,num_items)
        #url = 'http://www.metacritic.com/browse/movies/critic/name/{0}?num_items={1}'.format(letter,num_items)
            return url
        except TypeError: #proceed for publication_names starting from a number
            url = 'http://www.metacritic.com/browse/{0}/publication/name?num_items={1}'.format(filter,num_items)
            return url
    if publication_sort_by in ['popular','score']:
        url = 'http://www.metacritic.com/browse/{0}/publication/{1}?num_items={2}'.format(filter,publication_sort_by,num_items)
        return url
        
    #different filter_names for publication urls
    filter_dict = {
            'movies': 'movies',
            'games': 'games',
            'tv': 'tvshows',
            'music':'music'
        }
    filter = filter_dict[str.lower(filter_by)]
    url = 'http://www.metacritic.com/publication/{0}?filter={1}&num_items={2}&sort_options={3}&page={4}'            .format(publication_name,filter,num_items,sort_option,page_num)
    return url



#make 10 attempts to get the html of the provided url
def get_html(url, attempt=0):
    """
    This function makes 10 attempts to get the html document before raising the exception.
    Args:
        url: website url
    Returns:
        html document of url
    Exceptions:
        Raises exception 'Failed to fetch + url'
    """
    try:
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')
        opener = urllib2.build_opener()
        html_doc = opener.open(request).read()
        return html_doc
    except:
        if attempt > 10:
            raise Exception("Failed to fetch " + url)
        time.sleep(3)
        return get_html(url, attempt=attempt+1)


def get_soup(url):
    #header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    #html_doc = requests.get(url,headers = header).content.decode()
    html_doc = get_html(url)
    soup = BeautifulSoup(html_doc,'html.parser')
    return soup

def get_number_of_pages(soup):
    """
    returns number of pages for search if pagination available on current page.
    Args: 
        soup of html file using BeautifulSoup module of bs4 library
    Returns:
        number of pages in pagination
    """
    try:
        page_list = soup.find('li',{'class':'page last_page'})
        pages = int(page_list.find('a').getText())
        #print pages    
        return pages
    except AttributeError:
        #pagination not available, return single page
        return 1

#can be extended for movies, games, TV, music etc
def get_publication_names(letter='-1',category='movies', select_by = 'name'):
    """
    function returns critic names to be used for generating url to get critic reviews data
    Args: 
        letter: a single character or any number
            DEFAULT value 'a'
        category: one of ['movies','games','tv','music']
            DEFAULT value 'movies'
        select_by: filter publications based on 'Average Score','Most Popular' or 'Name'; valid values ['score','popular','name']
            DEFAULT value 'name'
    Returns:
        List of all publication names by provided argument
        
    """
    
    if letter == '-1' and select_by == 'name':
        raise Exception('InvalidInput: You must provide a valid letter when browsing publications by name.\
                        \nValid Input is any number (0-9) or any alphabet (a-z)')

    
    select_dict = {'score':'Average score','popular':'Most Popular','name': 'Name'}
    if select_by in ['score','popular']:
        print 'Start: Fetching publications by {} and category: {}...'.format(select_dict[select_by],category)
        url = get_url(filter_by=category,publication_sort_by=select_by)
    else:
        print 'Start: Fetching publications by {}, letter: {} and category: {}...'.format(select_dict[select_by],letter,category)
        url = get_url(letter,filter_by=category,publication_sort_by=select_by)
        
    soup = get_soup(url)
    pages = get_number_of_pages(soup)
    
    print 'Number of pages to fetch: {}'.format(pages)

    #check for publication listings on the page
    
    try: #no publication list on the page
        no_result1 = soup.find('p',{'class':'no_data'}).getText().strip()
        if no_result1 == 'No Results Found':
            print 'No Results found for name: {} and category: {}\nExiting the page.'.format(letter,category)
            return
    except: #publication listing found on the page
        pass
    #At the time of creation of this script, movie page have different div-class for 'No Results Found' than rest of the pages.
    #the below try-except covers this
    try: #no publication listing on movies page
        no_result2 = soup.find('div',{'class':'pad_top1'}).getText().strip()
        if no_result2 == 'No Results Found':
            print 'No Results found for name: {} and category: {}\nExiting the page.'.format(letter,category)
            return
    except: #publication listing found on the page
        pass
    
    publications = []
    for page in range(pages):
        print 'Fetching page {} of {}...'.format(page+1,pages)
        new_url = url + '&page='+str(page)
        new_soup = get_soup(new_url)
        
        publication_elements = new_soup.find_all('div',{'class':'title'})
            
        #seperate publication_name from publication url
        for publication_element in publication_elements:
            publication_name = {}
            try:
                link_element = publication_element.find('a',href = True)
                name = link_element['href'].replace('/publication/','')
                name = name[:name.find('?')].strip()
                publication_name['publication_name'] = name
                publication_name['category'] = category
                #print 'name: ',name
            except: #publication name not available
                continue
            publications.append(publication_name)
            
    print 'Success: Fetching publications complete.'
    return publications


#get all the critic data by publication
#can be extended for filter_by 'movies',games, tv, music etc
def get_all_critic_reviews(publication_name,category = 'movies',sort_by = 'critic_score'):
    """
    Collects all critic reviews by critic working for publication for a given category.
    Args: 
        publication_names: gets a list of publication names for which reviews are to be extracted
        category: one of ['movies','games','tv','music']
        sort_by: one of ['critic_score','date','metascore']
    Returns:
        A json object containing all critic reviews
    
    """
    
    print 'Start: Fetching critic reviews by publications for category: {} and sorted_by: {}...'.format(category,sort_by)
    final_result = []
    #for name in publication_names:
    print 'Start: Fetching reviews by publication: {}...'.format(publication_name)
    url = get_url(publication_name = publication_name,filter_by = category,sort_option= sort_by)
    #print url
    soup = get_soup(url)
        
    reviews = dict()
    pub_name = soup.find('h2',{'class':'module_title'}).getText().strip()
    pub_name = pub_name[:pub_name.find("'")]
    reviews['publication_name'] = pub_name
    #try:
    #    publication_title = soup.find('div',{'class':'publication_title'})
    #    reviews['publication_title'] = publication_title.find('a').getText().strip()
    #except:
    #    reviews['publication_title'] = None
            
    try:
        total_reviews = soup.find('div',{'class':'reviews_total'})
        reviews['total_reviews'] = total_reviews.find('a').getText().strip()
    except:
        reviews['total_reviews'] = None
        
    #print 'cname: {}, pTitle: {}, totalReviews: {}'.format(reviews['critic_name'],reviews['publication_title'],reviews['total_reviews'])
    
    reviews['reviews'] = get_reviews_by_critic(url,publication_name = publication_name,category = category,sort_by=sort_by)
    
    final_result.append(reviews)
    #break
        
    print 'Success: Fetching Reviews complete.'

    return final_result
	

#this function gets all reviews data related to the critic page
def get_reviews_by_critic(url,publication_name,category = 'movies',sort_by = 'critic_score'):
    """
    Collects all critic reviews page by page for give category and publication_name.
    Args: 
        url: url of the webpage
        publication_name: single publication name for which reviews are to be extracted
        category: one of ['movies','games','tv','music']
        sort_by: one of ['critic_score','date','metascore']
    Returns:
        A json object containing critic reviews of publication
    """
    
    soup = get_soup(url)
    pages = get_number_of_pages(soup)
    print 'Number of pages to fetch: {}'.format(pages)
    
    all_reviews = []

    for page in range(pages):
        print 'Fetching page {} of {}...'.format(page+1,pages)
        
        new_url = get_url(publication_name=publication_name,page_num=page,filter_by=category,sort_option=sort_by)
        #print url
        new_soup = get_soup(new_url)
        for review in new_soup.find_all('div',{'class':'review_wrap'}):
            #print review
            review_dict = dict()
            try:
                review_dict[category] = review.find('div',{'class':'review_product'}).find('a').getText().strip()
            except: #movie name is empty
                review_dict[category] = None
            try:
                meta_element = review.find('li',{'class':re.compile(r".*\bbrief_metascore\b.*")})
                metascore = meta_element.find('span',{'class':re.compile(r".*\bmetascore_w\b.*")}).getText().strip()
                review_dict['metascore'] = int(metascore)
            except ValueError: 
                if str(metascore) == 'tbd' and sort_by =='metascore': #no further metascore present
                    print 'TBD reached: Stop looking for more metascores'
		    return all_reviews
                else:
                    review_dict['metascore'] = None
            
            try:   
                critic_element = review.find('li',{'class':re.compile(r".*\bbrief_critscore\b.*")})
                critic_score = critic_element.find('span',{'class':re.compile(r'.*\bmetascore_w\b.*')}).getText().strip()
                review_dict['critic_score'] = int(critic_score)
            except ValueError: #no criticscore present
                if str(critic_score) =='tbd' and sort_by =='critic_score': #no further critic scores present
                    print 'TBD reached: Stop looking for more critic scores'
		    return all_reviews
                else:
                    review_dict['critic_score'] = None
            try:
                review_dict['critic_name'] = critic_element.find('a').getText().strip()
            except:
                review_dict['critic_name'] = 'Unknown'

            try:
                review_dict['review_desc'] = review.find('div',{'class':'review_body'}).getText().strip()
            except: #review description is empty
                review_dict['review_desc'] = None
            try:
                review_dict['post_date'] = review.find('li',{'class':'review_action post_date'}).getText().replace('Posted','').strip()
            except: #no post date present
                review_dict['post_date'] = None
            #print '(Movie: {}\tmetascore: {}\tCritScore: {}\tDesc: {}\tpostDate: {})'.format(review_dict['movie'],review_dict['metascore'],review_dict['score'],review_dict['review_desc'],review_dict['post_date'])

            all_reviews.append(review_dict)

    return all_reviews
