
.. _getting_started_header:

Getting Started
===============

Welcome to ``polygon``. Read this page to quickly install and configure this library to write your first Polygon 
Python application.

**It is highly recommended to read this page for everyone since it contains everything you need to get started with the library**

You can see some examples on the `github repository <https://github.com/pssolanki111/polygon/tree/main/EXAMPLES>`__ after you have done
the initial steps. And maybe join our `Discord Server <https://discord.gg/jPkARduU6N>`__ while you're at it :D

What you need to have
---------------------

1. A `polygon.io account <https://polygon.io/>`__ and your ``API key``. Find your api key on `Your Dashboard <https://polygon.io/dashboard/api-keys>`__
#. Python version 3.6 or higher. Don't have it installed? `Install python <https://www.python.org/downloads/>`__

Once you have these, Proceed to the installation of the library. Skip if already done.

Installing ``polygon``
----------------------

The recommended method of installation for all users is to install using ``pip`` from PyPi. A virtual environment is highly recommended but not a necessity.

run the below command in terminal (same for all OS)

.. code-block:: shell

  pip install polygon

To confirm the install worked, try importing the package as such

.. code-block:: python

  import polygon

If this doesn't throw any errors, the install worked. You may proceed to next steps now.

.. _create_and_use_header:

General guide for clients & functions
-------------------------------------
This section would provide general guidance on the clients without going into specific endpoints as stocks or options.

As you already know polygon.io has two major classes of APIs. The ``REST`` APIs and ``websockets`` streaming APIs.

This library implements all of them.

- For `REST HTTP endpoints <https://polygon.io/docs/getting-started>`__

  + Regular client is implemented for all endpoints.
  + Support for ``async`` client is also provided. See :ref:`async_support_header` for more.

- For `websocket streaming endpoints <https://polygon.io/docs/websockets/getting-started>`__

  + a ``callback`` based stream client is implemented. See :ref:`callback_streaming_header`
  + an async based stream client is also implemented. See :ref:`async_streaming_header`

Be sure to check out our special section :ref:`enums_header` for info on ``enums`` which will be used in many functions in this library to avoid passing error prone data.

Functions which are standalone (not attached to client objects) are all available at the top level as ``polygon.function_name``. 

**A detailed description of how to use the streaming endpoints is provided in the streamer docs linked above.**

Need examples? The `github repository <https://github.com/pssolanki111/polygon/tree/main/EXAMPLES>`__ has a few you could use.

**also feel free to join in our** `Discord Server <https://discord.gg/jPkARduU6N>`__ **to ask a question or just chat with interesting people**

Creating and Using REST HTTP clients
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This section aims to outline the general procedure to create and use the http clients in both regular and async programming methods.

First up, you'd import the library. There are many ways to import names from a library and it is highly recommended to complete fundamental python if you're not aware of them.

.. code-block:: python

  import polygon

  # OR import the name you need
  from polygon import StocksClient

  # OR import the names you need
  from polygon import (StocksClient, ForexClient, StreamClient, build_option_symbol)

Now creating a client is as simple as (using stocks and forex clients as examples here)

1. Regular client: ``stocks_client = polygon.StocksClient('API_KEY')``
#. Async client: ``forex_client = polygon.ForexClient('API_KEY', True)``

Note that It is NOT recommended to hard code your API key or other credentials into your code unless you really have a use case.
Instead preferably do one of the following:

1. create a separate python file with credentials, import that file into main file and reference using variable names.
#. Use environment variables.

Request timeouts and limits configuration (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**section Only meant for advanced use cases**. For most people, default timeouts would be enough.

You can also specify timeouts on requests. By default the timeout is set to 10 seconds for connection, read, write and pool timeouts.

**write timeout and pool timeout are only available for async rest client (which is httpx based)**. They'll be ignored if used with normal client

If you're unsure of what this implies, you probably don't need to change them.

**Limits config**

    Only meant for async rest client (httpx based).

    You also have the ability to change httpx connection pool settings when you work with async based rest client. This allows you to better control
    the behavior of underlying httpx pool, especially in cases where you need highly concurrent async applications.
    Using `uvloop <https://github.com/MagicStack/uvloop>`__ is also a good option in those case

    You can change the below configs:

    * **max_connections**: the max number of connections in the pool. Defaults to No Limit in the lib.
    * **max_keepalive**: max number of keepalive connections in the pool. Defaults to 30.

Example uses:

.. code-block:: python

  # client with a custom timeout. Default is 10 seconds
  client = polygon.StocksClient('api_key', connect_timeout=15)

  # another one
  client = polygon.StocksClient('api_key', connect_timeout=5, read_timeout=5)

  # An async one now
  client = polygon.StocksClient('key', True, read_timeout=5, connect_timeout=15)

  # another async one
  client = polygon.StocksClient('key', True, connect_timeout=15, max_connections=200)


Now that you have a client, simply call its methods to get data from the API

.. code-block:: python

  current_price = stocks_client.get_current_price('AMD')
  print(f'Current price for AMD is {current_price}')


**Note that you can have instances of all 5 different types of http clients together**. So you can create client for each one of the stocks, options and other APIs

All the clients in the lib support context managers

.. code-block:: python

  with polygon.StocksClient('KEY') as client:
      last_quote = client.get_last_quote('AMD)
      print(f'Last quote for AMD: {last_quote}')

  # OR for async
  async with polygon.StocksClient('key', True) as client:
      last_quote = await client.get_last_quote('AMD')
      print(last_quote)


Using context managers ensures that the connections opened up to make requests are closed properly.

You can manually close the connections if you're not using context managers:

1. for regular non-async: ``client.close()``
#. for async: ``await client.close()``

This is not an absolute necessity but rather a good software practice to close out resources when you don't need them.

Calling the methods/functions
-----------------------------

Most methods and functions have sane default values which can be customized as needed. Required parameters need to be
supplied as positional arguments (which just means that the order of arguments matter when passing more than one).

Some options, crypto and forex endpoints expect you to append prefixes ``O:, C:, X:`` respectively in front of tickers (on options symbols,
forex pairs and crypto pairs). **the library handles this for you** so you can pass in those with or without the prefix.

**Parameters which have special values are supplied as python enums**. You can however always pass in your own values
but it is recommended to use enums as they mitigate the possibilities of an error.

All enums are available in the module ``polygon.enums`` and can be imported the way you like.

If you're still unsure about enums, see our dedicated section: :ref:`enums_header`

Passing dates, datetime values or timestamps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The library allows you to specify your datetime or date values as ``datetime.date``, ``datetime.datetime`` objects or as
string ``YYYY-MM-DD``. Some endpoints also accept millisecond/nanosecond timestamps (docs will mention this wherever necessary)

- If an endpoint accepts a timestamp, you can either pass a timestamp or a datetime or date object. The lib will do the conversions for you
  internally

- When you pass a timestamp, library will NOT do any conversions and pass it as is. So make sure you are passing the correct timestamps.

- If you pass a ``datetime`` object, and the endpoint accepts a timestamp, the lib will convert internally to a timestamp. If there is no
  timezone info attached to the object, ``UTC`` will be used.

- If you come across situations where the returned data results are not complete or missing some values (for eg on aggregate bars endpoint),
  just pass your values as ``datetime`` values (if possible as a timestamp or with timezone information at least)

- The lib makes its best efforts parsing what the supplied datetime/timestamp/date could mean in context of the relevant endpoint. The behavior is of course
  different between for example aggs and trades. If you want absolute control, just pass as a unix timestamp or a ``datetime`` object having timezone information

Here are some **best practices when passing datetime or dates or timestamps**

-  If you want complete control over what's passed, pass a timestamp since epoch. The accuracy (i.e milli second or nano second)
   depends on the endpoint itself (mentioned in the docs of course). Default timestamp accuracy is ``ms``
-  Passing ``datetime`` objects is also a good way to pass absolute values and is recommended. Even better if the object has timezone info.
   If no timezone info is provided, lib assumes UTC. It doesn't make a difference in most cases, but should be taken care of in fine tuning and accurate filtering scenarios


Return Values
-------------

Most methods would by default return a dictionary/list object containing the data from the API. If you need the underlying response object
you need to pass in ``raw_response=True`` in the function call. It might be useful for checking ``status_code`` or inspecting ``headers``.

For 99% users, the default should be good enough.

The underlying response object returned is ``requests.models.Response`` for regular client and ``httpx.Response`` for async client.
Using ``.json()`` on the response object gets you the data dict/list

Once you have the response, you can utilize the data in any way that you like. You can push it to a database,
`create a pandas dataframe <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.from_dict.html>`__, save it to a file
or process it the way you like.

Every method's documentation contains a direct link to the corresponding official documentation page where you can see what the keys in the response mean.

.. _pagination_header:

Pagination Support
------------------

So quite a few endpoints implement pagination for large responses and hence the library implements a very simple and convenient way to
get all the pages and merge responses internally to give you a single response with all the results in it.

The behavior is exactly the same for ALL endpoints which support pagination (docs will mention when an endpoint is paginated). Knowing
the functions and parameters once is enough for all endpoints.

**To enable pagination**

    you simply need to pass ``all_pages=True`` to enable pagination for the concerned endpoint. You can also pass ``max_pages=an integer`` to limit how many pages the lib will fetch
    internally. The default behavior is to fetch all available pages.

You can pass ``verbose=True`` if you want to know what's happening behind the scenes. It will print out status
messages about the pagination process.

You can further customize what kinda output you want to get. **you have three possible options to make use of pagination abilities** in the
library

Get a Single Merged Response (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recommended for most users. Using this method will give you all the pages, **merged into one single response** internally for your convenience, and you will get
all the results from all pages in one single list.

To use, simply pass ``all_pages=True``. you can optionally provide ``max_pages`` number too to limit how many pages to get.

for example, below examples will do the merging of responses internally for you

.. code-block:: python

  # assuming client is created already

  # This will pull ALL available tickers from reference APIs and merge them into a single list
  data = client.get_tickers(market='stocks', limit=1000, all_pages=True)

  # This will pull up to 4 available pages of tickers from reference APIs and merge them into a
  # single list
  data = client.get_tickers(market='stocks', limit=1000, all_pages=True, max_pages=5)


Get a List of all pages
~~~~~~~~~~~~~~~~~~~~~~~

Only for people who know they need it. what this method does is provide you with a list of all pages, WITHOUT merging them. so you'll basically get a list of all pages like so
``[page1_data, page2_data, page3_data]``.

By default each page element is the corresponding page's data itself. You can also customize it to get the underlying response objects (meant for advanced use cases)

To enable, as usual you'd pass in ``all_pages=True``. But this time you'll ask the lib not to merge the pages using ``merge_all_pages=False``. That's it.
as described above, to get underlying response objects, pass an additional ``raw_page_responses=True`` too.

See examples below

.. code-block:: python

  # assuming client is created already

  # will fetch all available pages, won't merge them and return a list of responses
  data = client.get_tickers(market='stocks', limit=1000, all_pages=True, merge_all_pages=False)

  # will fetch all available pages, won't merge them and return a list of response objects
  data = client.get_tickers(market='stocks', limit=1000, all_pages=True, merge_all_pages=False,
                            raw_page_responses=True)

  # will fetch up to 5 available pages, won't merge them and return a list of responses
  data = client.get_tickers(market='stocks', limit=1000, all_pages=True, merge_all_pages=False,
                            max_pages=5)

Paginate Manually
~~~~~~~~~~~~~~~~~

Only meant for people who really need more manual control over pagination, yet want to make use of available functionality.

Every client has a few core methods which can be used to get next or previous pages by passing in the last response you have.

Note that while using these methods, you'd need to use your own mechanism to combine pages or process them.
If any of these methods return False, it means no more pages are available.

**Examples Use**

.. code-block:: python

  # assuming a client is created already
  data = client.get_trades(<blah-blah>)

  next_page_of_data = client.get_next_page(data)  # getting NEXT page
  previous_page_of_data = client.get_previous_page(data)  # getting PREVIOUS page

  # ASYNC examples
  await client.get_next_page(data)
  await client.get_previous_page(data)

  # It's wise to check if the value returned is not False.

**In practice, to get all pages (either next or previous), you'll need a while loop** An example:

.. code-block:: python

  all_responses = []

  response = client.get_trades_vx(<blah-blah>)  # using get_trades as example. you can use it on all methods which support pagination
  all_responses.append(response)  # using a list to store all the pages of response. You can use your own approach here.

  while 1:
      response = client.get_next_page(response)  # change to get_previous_page for previous pages.

      if not response:
          break

      all_responses.append(response)  # adding further responses to our list. you can use your own approach.

  print(f'all pages received. total pages: {len(all_responses)}')

.. _async_support_header:

Async Support for REST endpoints
--------------------------------

As you saw above in the example, the clients have methods for each endpoint. The usual client is a sync client.
However support for async is also provided for all the endpoints on all the clients.

Here is how to make use of it (**This info is applicable to ALL rest clients**)

First up, you'd create a client. Earlier you created a client by passing in just your API key. Here you'd create the client
with an additional argument.

so instead of something like: ``StocksClient('API_KEY')``, you'd do

.. code-block:: python

  client = StocksClient('KEY', True)   # or use_async=True for second parameter

This gives you an async client. Similar to sync, you can have all 5 different clients together. You can also pass in your timeout values like you
did above here too.

**ALL the methods you'd use for async client have the same names as their sync counterpart names.**

So if a method is named ``get_trades()`` in usual client, in async client you'd have it as ``get_trades()`` as well
and this behavior is true for all methods

Here is how you can use it grab the current price of a symbol

.. code-block:: python

  import polygon

  async def main():
      stocks_client = polygon.StocksClient('API_KEY', True)

      current_price = await stocks_client.get_current_price('AMD')
      print(current_price)

  if __name__ == '__main__':
      import asyncio
      asyncio.run(main())


UVLOOP integration
------------------

(for async streamer and async rest client)

unix based Operating systems only, `uvloop doesn't have windows support yet <https://github.com/MagicStack/uvloop/issues/14>`__

If your use case demands better performance on async streamer or async based applications using rest client than what the usual ``asyncio`` has to offer,
consider using `uvloop <https://github.com/MagicStack/uvloop>`__, a ``libuv`` based event loop which provides faster execution.

Using it is very simple, install using ``pip install uvloop`` and then **at the very top of your program**, right below your imports, add:

.. code-block:: python

  import uvloop

  asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

That's it. asyncio will now use uvloop's event loop policy instead of the default one.

Special Points
--------------

* Any method/endpoint having ``vX`` in its name is deemed experimental by polygon and its name and underlying URL path will be changed to a
  version number in the future. If you do use one of these, be aware of that name change which is reflected in the docs. If you find the lib
  doesn't have the changes reflected, let me know through any means mentioned in the help page.
* You would notice some parameters having ``lt``, ``lte``, ``gt`` and ``gte`` in their names. Those parameters are supposed to be filters for
  ``less than``, ``less than or equal to``, ``greater than``, ``greater than or equal to`` respectively. To know more see heading **Query Filter Extensions**
  in `This blog post by polygon <https://polygon.io/blog/api-pagination-patterns/>`__
  To explain: imagine a parameter: ``fill_date_lt``. now the date you'll supply would be a filter for values less than the given value and hence you'd get results which have fill_date
  less than your specified value, which in this case is a date.
* Some endpoints may not return a dictionary and instead return a ``list``. The number of such endpoints is very low. Similarly get current price returns a float/integer.
  I'm working towards reflecting the same in individual method's docs.
* It is highly recommended to use the polygon.io documentation website's quick test functionality to play around with the endpoints.
* Type hinting in function/method definitions indicate what data type does that parameter is supposed to be. If you think the type hinting is incomplete/incorrect, let me know.
  For example you might ses: ``cost: int`` which means this parameter ``cost`` is supposed to be an integer. ``adjusted: bool`` is another example for a boolean (either ``True`` or ``False``)
* You'll notice some type hints having ``Union`` in them followed by two or more types inside a square bracket. That simply means the parameter could be of any type from that list in bracket
  . For example: ``price: Union[str, float, int]`` means the parameter ``price`` could be either a string, a float or an integer. You'd notice Union type hints more on return types
  of the functions/methods.

**so far so good? Start by taking a look at the complete docs for endpoints you need. Here is a quick list**

* :ref:`stocks_header`
* :ref:`options_header`
* :ref:`forex_and_crypto_header`
* :ref:`callback_streaming_header` and :ref:`async_streaming_header`
* :ref:`bulk_data_download_header`
* :ref:`enums_header`
