from bs4 import BeautifulSoup as soup
import requests
import datetime
import re
import argparse
import csv

def get_page(url,params=None):
    """returns the content of a given url"""
    page = session.get(url,params=params,verify=False).content
    return page

def get_bsobj(page):
    """Returns a beautiful soup object of a given page"""
    bsobj = soup(page,"lxml")
    return bsobj

def get_divs(bsobj):
    """All information related to a single event in the page is
    contained in a div tage with class name "list-grid-item. Get all
    the div tags with this class name in a page and returns it"""

    all_divs = bsobj.find_all("div",attrs={"class":"list-grid-item"})
    if all_divs != []:
        return all_divs
    else:
        return None

def get_event_title(div):
    """Event title name and event url is contained in h3 tag with class name that
    contains "list-title. Find that tag and return event title and even name"""

    title_pattern = re.compile("list-title")
    title = div.find("h3",attrs={"class",title_pattern})
    event_title = None
    event_url   = None
    try:
        event_title = title.text.strip()
    except Exception:
        pass
    try:
        event_url = base_url+title.a["href"]
    except Exception:
        pass

    return event_title,event_url

def get_event_place(div):
    """name of the place, and website url of the place is contained in p tag
    with class name that contains serif in it, get name of place and url of place
    website from this tag and return it"""

    
    place_pattern = re.compile("serif")
    place = div.find("p",attrs={"class",place_pattern})
    place_name = None
    place_url  = None
    try:
        place_name = place.text.strip()
    except Exception:
        pass
    try:
        place_url_href = place.a["href"]
        place_url = (base_url + place_url_href).strip()
    except Exception:
        pass
    return place_name, place_url

def get_event_location(div):
    """Location name is contained in p tag with class name called styled, return
    text in that p tag"""

    location = div.find("p", attrs = {"class":"styled"})
    location_name = None
    try:
        location_name = location.text.strip()
    except Exception:
        pass
    return location_name

def get_event_date(div):

    """event date is contained in div tag with class name list-info,
    return the text in that div tag"""

    date = div.find("div", attrs = {"class":"list-info"})
    date_text = None
    try:
        date_text = date.text.replace("Date:","").strip()
    except Exception:
        pass
    return date_text

def get_event_time(div):
    """event time is present in div tag with class name "list-info mb-2,
    return text in that div tag
    """
    time  = div.find("div", attrs = {"class":"list-info mb-2"})
    time_text = None
    try:
        time_text = time.text.replace("Time: ","").strip()
    except Exception:
        pass
    return time_text

def collect_info(div):
    """Collect all the required information from the given div tag with class name
    list-grid-item """
    title,event_url = get_event_title(div)
    place_name,place_url = get_event_place(div)
    place_address   = get_event_location(div)
    event_date = get_event_date(div)
    event_time =  get_event_time(div)
    info_list = [title,event_url,place_name,place_url,place_address,event_date,event_time]
    # if all items are NONE return None, else return info_list
    if all(item is None for item in info_list):
        return None
    else:
        return info_list

def get_str_dates(additional_days):
    """returns two dates -start date and end dates, in str format of "mm/dd/yyyy",
    where two days are seperated by additional_days"""

    today = datetime.datetime.today()
    end_date = today+datetime.timedelta(days=additional_days)
    today_str = today.strftime("%m/%d/%Y")
    end_date_str = end_date.strftime("%m/%d/%Y")

    return today_str, end_date_str

def write_to_csv(event_list, output_name = "output.csv"):
    headers = ["Event_Title","Event_url","Place_name","Place_url","Location","event_date",
    "Event_time"]

    final_list  = [headers]+event_list
    with open(output_name,"w") as f:
        writer = csv.writer(f)
        writer.writerows(final_list)

def main():
    url = "https://www.visitindy.com/indianapolis-things-to-do-events"
    global base_url
    base_url = "https://www.visitindy.com"


    all_events = []

    #start a requests session
    session = requests.session()

    #get beautiful soup object of the page
    bsobj = get_bsobj(session.get(url).content)

    #number of pages to navigate in the website
    pages_to_navigate = 10

    for page_num in range(pages_to_navigate):
        values = {
        "authenticity_token": bsobj.find(attrs={"name":"authenticity_token"})["value"],
        "search_whattodo_from": start_date,
        "search_whattodo_to": end_date,
        "search_sort": "date_sort",
        "page" :page_num + 1
        }

        page = session.post(url,data=values,verify=False).content
        bsobj = get_bsobj(page)
        divs = get_divs(bsobj)

        if divs is not None:
            for i in divs:
                info = collect_info(i)
                if info is not None:
                    all_events.append(info)

        write_to_csv(all_events)

if __name__ == "__main__":
    #default start and end dates (today + 14 days from now)
    start_date,end_date = get_str_dates(14)

    parser = argparse.ArgumentParser(description="Takes the start date and end date")
    parser.add_argument("-sd","--startdate", type = str, help = "start date in mm/dd/yyyy format",default = start_date)
    parser.add_argument("-ed","--enddate",type = str, help = "end date in mm/dd/yyyy format",default = end_date)
    args = parser.parse_args()
    start_date = args.startdate
    end_date   = args.enddate
    main()
