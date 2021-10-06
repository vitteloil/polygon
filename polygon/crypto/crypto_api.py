# ========================================================= #
import requests
import httpx
from typing import Union
import datetime
from requests.models import Response
from httpx import Response as HttpxResponse
# ========================================================= #


class CryptoClient:
    """
    These docs are not meant for general users. These are library API references. The actual docs will be
    available on the index page when they are prepared.

    This class implements all the crypto REST endpoints. Note that you should always import names from top level.
    eg: ``from polygon import CryptoClient`` or ``import polygon` (which allows you to access all names easily)

    Creating the client is as simple as: ``client = CryptoClient('MY_API_KEY')``
    Once you have the client, you can call its methods to get data from the APIs. All methods have sane default
    values and almost everything can be customized.

    Any method starting with ``async_`` in its name is meant to be for async programming. All methods have their sync
    and async counterparts. Any async method must be awaited while non-async (or sync) methods should be called
    directly.

    Type Hinting tells you what data type a parameter is supposed to be. You should always use ``enums`` for most
    parameters to avoid supplying error prone values.

    It is also a good idea to visit the `official documentation <https://polygon.io/docs/getting-started>`__. This
    page has all the endpoints. I highly recommend using the UI there to play with the endpoints a bit. Observe the
    data you receive as the actual data received through python lib is exactly the same as shown on their page when
    you click ``Run Query``.
    """
    def __init__(self, api_key: str, use_async: bool = False):
        """
        Initiates a Client to be used to access all the endpoints.

        :param api_key: Your API Key. Visit your dashboard to get yours.
        :param use_async: Set to True to get an async client. Defaults to False which returns a non-async client.
        """
        self.KEY, self._async = api_key, use_async
        self.BASE = 'https://api.polygon.io'

        if self._async:
            self.session = httpx.AsyncClient()
        else:
            self.session = requests.session()

        self.session.headers.update({'Authorization': f'Bearer {self.KEY}'})

    # Context Managers
    def __enter__(self):
        if not self._async:
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._async:
            self.session.close()

    # Context Managers - Asyncio
    async def __aenter__(self):
        if self._async:
            return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._async:
            self.session: httpx.AsyncClient
            await self.session.aclose()

    def close(self):
        """
        Closes the ``requests.Session`` and frees up resources. It is recommended to call this method in your
        exit handlers

        Note that this is meant for sync programming only. Use :meth:`async_close` for async.

        :return: None
        """
        if not self._async:
            self.session.close()

    async def async_close(self):
        """
        Closes the ``httpx.AsyncClient`` and frees up resources. It is recommended to call this method in your
        exit handlers. This method should be awaited as this is a coroutine.

        Note that this is meant for async programming only. Use :meth:`close` for sync.

        :return: None
        """
        if self._async:
            self.session: httpx.AsyncClient
            await self.session.aclose()

    # Internal Functions
    def _get_response(self, path: str, params: dict = None,
                      raw_response: bool = True) -> Union[Response, dict]:
        """
        Get response on a path. Meant to be used internally but can be used if you know what you're doing. To be
        used by sync client only. For async access, see :meth:`_get_async_response`

        :param path: RESTful path for the endpoint. Available on the docs for the endpoint right above its name.
        :param params: Query Parameters to be supplied with the request. These are mapped 1:1 with the endpoint.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to check the
                             status code or inspect the headers. Defaults to True which returns the ``Response`` object.
        :return: A Response object by default. Make ``raw_response=False`` to get JSON decoded Dictionary
        """
        _res = self.session.request('GET', self.BASE + path, params=params)

        if raw_response:
            return _res

        return _res.json()

    async def _get_async_response(self, path: str, params: dict = None,
                                  raw_response: bool = True) -> Union[HttpxResponse, dict]:
        """
        Get response on a path - meant to be used internally but can be used if you know what you're doing - to be
        used by async client only. For sync access, see :meth:`_get_response`

        :param path: RESTful path for the endpoint. Available on the docs for the endpoint right above its name.
        :param params: Query Parameters to be supplied with the request. These are mapped 1:1 with the endpoint.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to check the
                             status code or inspect the headers. Defaults to True which returns the ``Response`` object.
        :return: A Response object by default. Make ``raw_response=False`` to get JSON decoded Dictionary
        """
        _res = await self.session.request('GET', self.BASE + path, params=params)

        if raw_response:
            return _res

        return _res.json()

    def get_next_page_by_url(self, url: str, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the next page of a response. The URl is returned within ``next_url`` attribute on endpoints which support
        pagination (eg the tickers endpoint). If the response doesn't contain this attribute, either all pages were
        received or the endpoint doesn't have pagination. Meant for internal use primarily.

        Note that this method is meant for sync programming. See :meth:`async_get_next_page_by_url` for async.

        :param url: The next URL. As contained in ``next_url`` of the response.
        :param raw_response: Whether or not to return the Response Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: Either a Dictionary or a Response object depending on value of raw_response. Defaults to Dict.
        """
        _res = self.session.request('GET', url)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_next_page_by_url(self, url: str, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the next page of a response. The URl is returned within ``next_url`` attribute on endpoints which support
        pagination (eg the tickers endpoint). If the response doesn't contain this attribute, either all pages were
        received or the endpoint doesn't have pagination. Meant for internal use primarily.

        Note that this method is meant for async programming. See :meth:`get_next_page_by_url` for sync.

        :param url: The next URL. As contained in ``next_url`` of the response.
        :param raw_response: Whether or not to return the Response Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: Either a Dictionary or a Response object depending on value of raw_response. Defaults to Dict.
        """
        _res = await self.session.request('GET', url)

        if raw_response:
            return _res

        return _res.json()

    # Endpoints
    def get_historic_trades(self, from_symbol: str, to_symbol: str, date, offset: Union[str, int] = None,
                            limit: int = 500, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get historic trade ticks for a cryptocurrency pair.
        `Official Docs
        <https://polygon.io/docs/get_v1_historic_crypto__from___to___date__anchor>`__

        :param from_symbol: The "from" symbol of the crypto pair.
        :param to_symbol: The "to" symbol of the crypto pair.
        :param date: The date/day of the historic ticks to retrieve. Could be ``datetime``, ``date`` or string
                     ``YYYY-MM-DD``
        :param offset: The timestamp offset, used for pagination. This is the offset at which to start the results.
                       Using the timestamp of the last result as the offset will give you the next page of results.
                       I'm trying to  think of a good way to implement pagination in the library for these endpoints
                       which do not return a ``next_url`` attribute.
        :param limit: Limit the size of the response, max 10000. Default 500
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        if isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
            date = date.strftime('%Y-%m-%d')

        _path = f'/v1/historic/crypto/{from_symbol.upper()}/{to_symbol.upper()}/{date}'

        _data = {'offset': offset,
                 'limit': limit}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_last_trade(self, from_symbol: str, to_symbol: str, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the last trade tick for a cryptocurrency pair.
        `Official Docs
        <https://polygon.io/docs/get_v1_last_crypto__from___to__anchor>`__

        :param from_symbol: The "from" symbol of the pair.
        :param to_symbol: The "to" symbol of the pair.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v1/last/crypto/{from_symbol.upper()}/{to_symbol.upper()}'

        _res = self._get_response(_path)

        if raw_response:
            return _res

        return _res.json()

    def get_daily_open_close(self, from_symbol: str, to_symbol: str, date, adjusted: bool = True,
                             raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the open, close prices of a cryptocurrency symbol on a certain day.
        `Official Docs: <https://polygon.io/docs/get_v1_open-close_crypto__from___to___date__anchor>`__

        :param from_symbol: The "from" symbol of the pair.
        :param to_symbol: The "to" symbol of the pair.
        :param date: The date of the requested open/close. Could be ``datetime``, ``date`` or string ``YYYY-MM-DD``.
        :param adjusted: Whether or not the results are adjusted for splits. By default, results are adjusted. Set this
                         to False to get results that are NOT adjusted for splits.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v1/open-close/crypto/{from_symbol.upper()}/{to_symbol.upper()}/{date}'

        _data = {'adjusted': 'true' if adjusted else 'false'}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_aggregate_bars(self, symbol: str, from_date, to_date, multiplier: int = 1, timespan: str = 'day',
                           adjusted: bool = True, sort: str = 'asc', limit: int = 5000,
                           raw_response: bool = False) -> Union[Response, dict]:
        """
        Get aggregate bars for a cryptocurrency pair over a given date range in custom time window sizes.
        For example, if ``timespan=‘minute’`` and ``multiplier=‘5’`` then 5-minute bars will be returned.
        `Official Docs
        <https://polygon.io/docs/get_v2_aggs_ticker__cryptoTicker__range__multiplier___timespan___from___to__anchor>`__

        :param symbol: The ticker symbol of the currency pair. eg: ``X:BTCUSD``
        :param from_date: The start of the aggregate time window. Could be ``datetime``, ``date`` or string
                          ``YYYY-MM-DD``
        :param to_date: The end of the aggregate time window. Could be ``datetime``, ``date`` or string ``YYYY-MM-DD``
        :param multiplier: The size of the timespan multiplier
        :param timespan: The size of the time window.
        :param adjusted: Whether or not the results are adjusted for splits. By default, results are adjusted.
                         Set this to False to get results that are NOT adjusted for splits.
        :param sort: Order of sorting the results. See :class:`polygon.enums.SortOrder` for available choices.
                     Defaults to ``asc`` (oldest at the top)
        :param limit: Limits the number of base aggregates queried to create the aggregate results. Max 50000 and
                      Default 5000.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        if isinstance(from_date, datetime.datetime) or isinstance(from_date, datetime.date):
            from_date = from_date.strftime('%Y-%m-%d')

        if isinstance(to_date, datetime.datetime) or isinstance(to_date, datetime.date):
            to_date = to_date.strftime('%Y-%m-%d')

        _path = f'/v2/aggs/ticker/{symbol.upper()}/range/{multiplier}/{timespan}/{from_date}/{to_date}'

        _data = {'adjusted': 'true' if adjusted else 'false',
                 'sort': sort,
                 'limit': limit}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_grouped_daily_bars(self, date, adjusted: bool = True, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the daily open, high, low, and close (OHLC) for the entire cryptocurrency market.
        `Official Docs <https://polygon.io/docs/get_v2_aggs_grouped_locale_global_market_crypto__date__anchor>`__

        :param date: The date for the aggregate window. Could be ``datetime``, ``date`` or string ``YYYY-MM-DD``
        :param adjusted:  Whether or not the results are adjusted for splits. By default, results are adjusted. Set
                          this to False to get results that are NOT adjusted for splits.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        if isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
            date = date.strftime('%Y-%m-%d')

        _path = f'/v2/aggs/grouped/locale/global/market/crypto/{date}'

        _data = {'adjusted': 'true' if adjusted else 'false'}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_previous_close(self, symbol: str, adjusted: bool = True,
                           raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the previous day's open, high, low, and close (OHLC) for the specified cryptocurrency pair.
        `Official Docs <https://polygon.io/docs/get_v2_aggs_ticker__cryptoTicker__prev_anchor>`__

        :param symbol: The ticker symbol of the currency pair.
        :param adjusted: Whether or not the results are adjusted for splits. By default, results are adjusted. Set this
                         to False to get results that are NOT adjusted for splits.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make `raw_response=True` to get underlying response object
        """

        _path = f'/v2/aggs/ticker/{symbol.upper()}/prev'

        _data = {'adjusted': 'true' if adjusted else 'false'}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_snapshot_all(self, symbols: list, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the current minute, day, and previous day’s aggregate, as well as the last trade and quote for all traded
        cryptocurrency symbols
        `Official Docs <https://polygon.io/docs/get_v2_snapshot_locale_global_markets_crypto_tickers_anchor>`__

        :param symbols: A list of tickers to get snapshots for.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make `raw_response=True` to get underlying response object
        """

        if not isinstance(symbols, list):
            raise ValueError('symbols must be supplied as a list of tickers')

        _path = f'/v2/snapshot/locale/global/markets/crypto/tickers'

        _data = {'tickers': ','.join([x.upper() for x in symbols])}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_snapshot(self, symbol: str, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the current minute, day, and previous day’s aggregate, as well as the last trade and quote for a single
        traded cryptocurrency symbol.
        `Official Docs <https://polygon.io/docs/get_v2_snapshot_locale_global_markets_crypto_tickers__ticker__anchor>`__

        :param symbol: Symbol of the currency pair
        :param raw_response: Whether or not to return the Response Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make `raw_response=True` to get underlying response object
        """

        _path = f'/v2/snapshot/locale/global/markets/crypto/tickers/{symbol.upper()}'

        _res = self._get_response(_path)

        if raw_response:
            return _res

        return _res.json()

    def get_gainers_and_losers(self, direction: str = 'gainers', raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the current top 20 gainers or losers of the day in cryptocurrency markets.
        `Official docs <https://polygon.io/docs/get_v2_snapshot_locale_global_markets_crypto__direction__anchor>`__

        :param direction: The direction of the snapshot results to return. See :class:`polygon.enums.SnapshotDirection`
                          for available choices. Defaults to Gainers.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v2/snapshot/locale/global/markets/crypto/{direction}'

        _res = self._get_response(_path)

        if raw_response:
            return _res

        return _res.json()

    def get_level2_book(self, symbol: str, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the current level 2 book of a single ticker. This is the combined book from all of the exchanges.
        `Official Docs
        <https://polygon.io/docs/get_v2_snapshot_locale_global_markets_crypto_tickers__ticker__book_anchor>`__

        :param symbol: The cryptocurrency ticker.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v2/snapshot/locale/global/markets/crypto/tickers/{symbol.upper()}/book'

        _res = self._get_response(_path)

        if raw_response:
            return _res

        return _res.json()

    # ASYNC Operations' Methods
    async def async_get_historic_trades(self, from_symbol: str, to_symbol: str,
                                        date, offset: Union[str, int] = None, limit: int = 500,
                                        raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get historic trade ticks for a cryptocurrency pair - Async method.
        `Official Docs
        <https://polygon.io/docs/get_v1_historic_crypto__from___to___date__anchor>`__

        :param from_symbol: The "from" symbol of the crypto pair.
        :param to_symbol: The "to" symbol of the crypto pair.
        :param date: The date/day of the historic ticks to retrieve. Could be ``datetime``, ``date`` or string
                     ``YYYY-MM-DD``
        :param offset: The timestamp offset, used for pagination. This is the offset at which to start the results.
                       Using the timestamp of the last result as the offset will give you the next page of results.
                       I'm trying to  think of a good way to implement pagination in the library for these endpoints
                       which do not return a ``next_url`` attribute.
        :param limit: Limit the size of the response, max 10000. Default 500
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        if isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
            date = date.strftime('%Y-%m-%d')

        _path = f'/v1/historic/crypto/{from_symbol.upper()}/{to_symbol.upper()}/{date}'

        _data = {'offset': offset,
                 'limit': limit}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_last_trade(self, from_symbol: str, to_symbol: str,
                                   raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the last trade tick for a cryptocurrency pair - Async method
        `Official Docs
        <https://polygon.io/docs/get_v1_last_crypto__from___to__anchor>`__

        :param from_symbol: The "from" symbol of the pair.
        :param to_symbol: The "to" symbol of the pair.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v1/last/crypto/{from_symbol.upper()}/{to_symbol.upper()}'

        _res = await self._get_async_response(_path)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_daily_open_close(self, from_symbol: str, to_symbol: str, date, adjusted: bool = True,
                                         raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the open, close prices of a cryptocurrency symbol on a certain day - Async method
        `Official Docs: <https://polygon.io/docs/get_v1_open-close_crypto__from___to___date__anchor>`__

        :param from_symbol: The "from" symbol of the pair.
        :param to_symbol: The "to" symbol of the pair.
        :param date: The date of the requested open/close. Could be ``datetime``, ``date`` or string ``YYYY-MM-DD``.
        :param adjusted: Whether or not the results are adjusted for splits. By default, results are adjusted. Set this
                         to False to get results that are NOT adjusted for splits.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v1/open-close/crypto/{from_symbol.upper()}/{to_symbol.upper()}/{date}'

        _data = {'adjusted': 'true' if adjusted else 'false'}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_aggregate_bars(self, symbol: str, from_date, to_date, multiplier: int = 1,
                                       timespan: str = 'day', adjusted: bool = True, sort: str = 'asc',
                                       limit: int = 5000, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        et aggregate bars for a cryptocurrency pair over a given date range in custom time window sizes.
        For example, if ``timespan=‘minute’`` and ``multiplier=‘5’`` then 5-minute bars will be returned - Async method
        `Official Docs
        <https://polygon.io/docs/get_v2_aggs_ticker__cryptoTicker__range__multiplier___timespan___from___to__anchor>`__

        :param symbol: The ticker symbol of the currency pair. eg: ``X:BTCUSD``
        :param from_date: The start of the aggregate time window. Could be ``datetime``, ``date`` or string
                          ``YYYY-MM-DD``
        :param to_date: The end of the aggregate time window. Could be ``datetime``, ``date`` or string ``YYYY-MM-DD``
        :param multiplier: The size of the timespan multiplier
        :param timespan: The size of the time window.
        :param adjusted: Whether or not the results are adjusted for splits. By default, results are adjusted.
                         Set this to False to get results that are NOT adjusted for splits.
        :param sort: Order of sorting the results. See :class:`polygon.enums.SortOrder` for available choices.
                     Defaults to ``asc`` (oldest at the top)
        :param limit: Limits the number of base aggregates queried to create the aggregate results. Max 50000 and
                      Default 5000.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        if isinstance(from_date, datetime.datetime) or isinstance(from_date, datetime.date):
            from_date = from_date.strftime('%Y-%m-%d')

        if isinstance(to_date, datetime.datetime) or isinstance(to_date, datetime.date):
            to_date = to_date.strftime('%Y-%m-%d')

        _path = f'/v2/aggs/ticker/{symbol.upper()}/range/{multiplier}/{timespan}/{from_date}/{to_date}'

        _data = {'adjusted': 'true' if adjusted else 'false',
                 'sort': sort,
                 'limit': limit}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_grouped_daily_bars(self, date, adjusted: bool = True,
                                           raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the daily open, high, low, and close (OHLC) for the entire cryptocurrency market - Async method
        `Official Docs <https://polygon.io/docs/get_v2_aggs_grouped_locale_global_market_crypto__date__anchor>`__

        :param date: The date for the aggregate window. Could be ``datetime``, ``date`` or string ``YYYY-MM-DD``
        :param adjusted:  Whether or not the results are adjusted for splits. By default, results are adjusted. Set
                          this to False to get results that are NOT adjusted for splits.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        if isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
            date = date.strftime('%Y-%m-%d')

        _path = f'/v2/aggs/grouped/locale/global/market/crypto/{date}'

        _data = {'adjusted': 'true' if adjusted else 'false'}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_previous_close(self, symbol: str, adjusted: bool = True,
                                       raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the previous day's open, high, low, and close (OHLC) for the specified cryptocurrency pair - Async method
        `Official Docs <https://polygon.io/docs/get_v2_aggs_ticker__cryptoTicker__prev_anchor>`__

        :param symbol: The ticker symbol of the currency pair.
        :param adjusted: Whether or not the results are adjusted for splits. By default, results are adjusted. Set this
                         to False to get results that are NOT adjusted for splits.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make `raw_response=True` to get underlying response object
        """

        _path = f'/v2/aggs/ticker/{symbol.upper()}/prev'

        _data = {'adjusted': 'true' if adjusted else 'false'}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_snapshot_all(self, symbols: list, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the current minute, day, and previous day’s aggregate, as well as the last trade and quote for all traded
        cryptocurrency symbols - Async method
        `Official Docs <https://polygon.io/docs/get_v2_snapshot_locale_global_markets_crypto_tickers_anchor>`__

        :param symbols: A list of tickers to get snapshots for.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make `raw_response=True` to get underlying response object
        """

        if not isinstance(symbols, list):
            raise ValueError('symbols must be supplied as a list of tickers')

        _path = f'/v2/snapshot/locale/global/markets/crypto/tickers'

        _data = {'tickers': ','.join([x.upper() for x in symbols])}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_snapshot(self, symbol: str, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the current minute, day, and previous day’s aggregate, as well as the last trade and quote for a single
        traded cryptocurrency symbol - Async method
        `Official Docs <https://polygon.io/docs/get_v2_snapshot_locale_global_markets_crypto_tickers__ticker__anchor>`__

        :param symbol: Symbol of the currency pair
        :param raw_response: Whether or not to return the Response Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make `raw_response=True` to get underlying response object
        """

        _path = f'/v2/snapshot/locale/global/markets/crypto/tickers/{symbol.upper()}'

        _res = await self._get_async_response(_path)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_gainers_and_losers(self, direction: str = 'gainers',
                                           raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the current top 20 gainers or losers of the day in cryptocurrency markets - Async method
        `Official docs <https://polygon.io/docs/get_v2_snapshot_locale_global_markets_crypto__direction__anchor>`__

        :param direction: The direction of the snapshot results to return. See :class:`polygon.enums.SnapshotDirection`
                          for available choices. Defaults to Gainers.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v2/snapshot/locale/global/markets/crypto/{direction}'

        _res = await self._get_async_response(_path)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_level2_book(self, symbol: str, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the current level 2 book of a single ticker. combined book from all of the exchanges - Async method
        `Official Docs
        <https://polygon.io/docs/get_v2_snapshot_locale_global_markets_crypto_tickers__ticker__book_anchor>`__

        :param symbol: The cryptocurrency ticker.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v2/snapshot/locale/global/markets/crypto/tickers/{symbol.upper()}/book'

        _res = await self._get_async_response(_path)

        if raw_response:
            return _res

        return _res.json()


# ========================================================= #


if __name__ == '__main__':
    print('Don\'t You Dare Running Lib Files Directly')


# ========================================================= #
