![poster](output/tube-map-poster.svg)

I wanted to decorate my apartment with a tube map just like the ones they have in stations. The [posters they sell](https://www.ltmuseumshop.co.uk/posters/transport/london-underground-tube-map-poster) are a different design and are not available in the same sort of size. TFL doesn't routinely release the station poster design digitally either.

Fortunately, TFL supplies copies in response to [FOI requests](https://tfl.gov.uk/corporate/transparency/freedom-of-information/foi-request-detail?referenceId=FOI-2379-1819)

Unfortunately, it's in the form of a lossy JPEG inside a PDF.

Fortunately, there exists an *extremely* good vectorizer called [Vector Magic](https://vectormagic.com/).

Unfortunately, it only supports inputs below 4 megapixels, and its batch mode isn't very configurable and can't use the same image color palette between runs.

Fortunately, computers have to do whatever we ask. So we use a user-space MachO loader and do some reverse engineering to [manually use invoke its vectorizer](tracer/go.py) in order to convert the whole map in chunks.

