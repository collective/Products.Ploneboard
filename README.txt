ATAmazon requires the Amazon web services library:

http://www.josephson.org/projects/pyamazon/

You will also need an Amazon Web Services developer key and an Amazon associate id.  
Be sure to set these values in portal_properties/site_properties After you install ATAmazon.

Adding here/portlet_amazon/macros/portlet to left_slots or right_slots will give you a
portlet that lists relevant books.

The books that appear in the portlet are obtained as follows:
1) First, published Amazon Items in the current_folder/.books/ are listed, 
   sorted by Amazon sales rank
2) Next, other published Amazon Items anywhere below current_folder are listed, 
   again sorted by Amazon sales rank
3) Finally published Amazon Items anywhere in the portal are listed,
   sorted by Amazon sales rank

The portal will show a total of 5 books, but this can be altered by customizing portlet_amazon