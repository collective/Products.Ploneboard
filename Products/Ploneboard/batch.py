from ExtensionClass import Base
from Products.CMFPlone.PloneBatch import Batch as PloneBatch,        \
                                         calculate_pagenumber,       \
                                         calculate_pagerange,        \
                                         calculate_leapback,         \
                                         calculate_leapforward
                                         
class LazyPrevBatch(Base):
    def __of__(self, parent):
        start = parent.first - parent._size + parent.overlap
        if start < 0 or start >= parent.sequence_length:
            return None
        return Batch(parent._method, parent.sequence_length, parent._size,
                     start, 0, parent.orphan, parent.overlap)

class LazyNextBatch(Base):
    def __of__(self, parent):
        start = parent.end - parent.overlap
        if start < 0 or start >= parent.sequence_length:
            return None
        return Batch(parent._method, parent.sequence_length, parent._size,
                     start, 0, parent.orphan, parent.overlap)

class Batch(PloneBatch):
    """A custom batch implementation to enable batching over forums and
    conversations. This is identical to PloneBatch's implementation except:
    
     - The sequence length is explicitly given to the constructor
     - Instead of operating on a sequence, the batch is given a method to call.
       This method needs to have a signature
       
            def getItems(self, limit, offset)
       
       limit is the number of items to return (the batch size) and offset is
       the number of items to skip at the beginning of the sequence.
    """
    __allow_access_to_unprotected_subobjects__ = 1
    
    # Needs first, length, 
    
    previous = LazyPrevBatch()
    next = LazyNextBatch()
    sequence_length = None
    
    size = first= start = end = orphan = overlap = navlist = None
    numpages = pagenumber = pagerange = pagerangeend = pagerangestart = pagenumber = quantumleap = None
    
    
    def __init__( self, method, sequence_length, size, start=0, end=0, orphan=0, overlap=0, pagerange=7, quantumleap=0, b_start_str='b_start'):
        """ Encapsulate sequence in batches of size
        method          - the method to call to get the correct part of the batch
        sequence_length - the total number of items in the sequence
        size            - the number of items in each batch. This will be computed if left out.
        start           - the first element of sequence to include in batch (0-index)
        end             - the last element of sequence to include in batch (0-index, optional)
        orphan          - the next page will be combined with the current page if it does not contain more than orphan elements
        overlap         - the number of overlapping elements in each batch
        pagerange       - the number of pages to display in the navigation
        quantumleap     - 0 or 1 to indicate if bigger increments should be used in the navigation list for big results.
        b_start_str     - the request variable used for start, default 'b_start'
        """
        start = start + 1

        self.sequence_length = sequence_length
        self._method = method

        start,end,sz = opt(start,end,size,orphan,sequence_length)
        
        self.size = sz
        self._size = size
        self.start = start
        self.end = end
        self.orphan = orphan
        self.overlap = overlap
        self.first = max(start - 1, 0)
        self.length = self.end - self.first
        
        self.b_start_str = b_start_str

        self.last = sequence_length - size

        # Set up next and previous
        if self.first == 0:
            self.previous = None

        # Set up the total number of pages
        self.numpages = calculate_pagenumber(self.sequence_length - self.orphan, self.size, self.overlap)

        # Set up the current page number
        self.pagenumber = calculate_pagenumber(self.start, self.size, self.overlap)

        # Set up pagerange for the navigation quick links
        self.pagerange, self.pagerangestart, self.pagerangeend = calculate_pagerange(self.pagenumber,self.numpages,pagerange)

        # Set up the lists for the navigation: 4 5 [6] 7 8
        #  navlist is the complete list, including pagenumber
        #  prevlist is the 4 5 in the example above
        #  nextlist is 7 8 in the example above
        self.navlist = self.prevlist = self.nextlist = []
        if self.pagerange and self.numpages >= 1:
            self.navlist  = range(self.pagerangestart, self.pagerangeend)
            self.prevlist = range(self.pagerangestart, self.pagenumber)
            self.nextlist = range(self.pagenumber + 1, self.pagerangeend)

        # QuantumLeap - faster navigation for big result sets
        self.quantumleap = quantumleap
        self.leapback = self.leapforward = []
        if self.quantumleap:
            self.leapback = calculate_leapback(self.pagenumber, self.numpages, self.pagerange)
            self.leapforward = calculate_leapforward(self.pagenumber, self.numpages, self.pagerange)

    def __getitem__(self, index):
        """ Pull an item out of the partial sequence that is this batch """
        if (index < 0 and index + self.end < self.first) or index >= self.length:
            raise IndexError, index
        sequence = getattr(self, '_partial_sequence', None)
        if sequence is None:
            self._partial_sequence = sequence = self._method(self.length, self.start-1)
        return sequence[index]

    def __len__(self):
        """ Get the length of the partial sequence that is this batch """
        return self.length

def opt(start, end, size, orphan, sequence_length):
    """Calculate start, end and batch size"""
    length = sequence_length
    if size < 1:
        if start > 0 and end > 0 and end >= start:
            size = end + 1 - start
        else: size = 25
    if start > 0: 
        if start>length: 
            start = length
        if end > 0:
            if end < start: end = start
        else:
            end = start + size - 1
            if (end+orphan)>=length:
                end = length
    elif end > 0:
        if (end)>length:
            end = length
        start = end + 1 - size
        if start - 1 < orphan: start = 1
    else:
        start = 1
        end = start + size - 1
        if (end+orphan)>=length:
            end = length
    return start,end,size
