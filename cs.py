from services.font_crawler_service import FontCrawlerService

font_cr = FontCrawlerService(crawl_url='https://www.fontshop.com/families/ff-meta', parent_folder='downloads')
font_cr.save_font_data()
