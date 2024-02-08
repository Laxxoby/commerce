from .models import User, Category, Auction_listings, watchlist, Bids

def obtener_ganador_de_subasta(producto):
    if producto.currentPrice is not None:
        ultima_puja = Bids.objects.filter(product=producto, bid=producto.currentPrice).first()
        if ultima_puja:
            ganador = ultima_puja.bidder
            return ganador
    
    return None
