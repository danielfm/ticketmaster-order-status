#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (c) 2009, Daniel Fernandes Martins
# All rights reserved.
#
# Redistribution and use of this software in source and binary forms, with or
# without modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the author name nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission of the author.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import optparse
import urllib
import urllib2
import pynotify


# Base URL
_BASE_URL = 'https://ticketing.ticketmaster.com.br'

# Authentication and order status URIs
_LOGIN_URI = '%s/shwLogin.cfm' % _BASE_URL
_ORDER_URI = '%s/shwCompraDetalhe.cfm?pedidoID=%%s' % _BASE_URL

# Order list link
_ORDERS_LINK = '<a href="%s">More</a>' % _LOGIN_URI

# Notification priorities
_PRIORITY_LOW      = pynotify.URGENCY_LOW
_PRIORITY_NORMAL   = pynotify.URGENCY_NORMAL
_PRIORITY_CRITICAL = pynotify.URGENCY_CRITICAL

# Notification messages to display according to the orders status
_NOTIFICATION_TITLE = 'Ticketmaster Order %s'
_STATUS_CODES = {
    'Livre'      : ('Order not processed yet', _PRIORITY_LOW),
    'StdReserva' : ('Reserving your tickets' , _PRIORITY_NORMAL),
    'StdCobranca': ('Charging your tickets'  , _PRIORITY_NORMAL),
    'VendaOk'    : ('Order billed'           , _PRIORITY_NORMAL),
    'Recusada'   : ('Order rejected'         , _PRIORITY_CRITICAL)
}


def initialize_notification_system(app_title):
    """
    Initializes the notification machinery.
    """
    if not pynotify.init(app_title):
        import sys
        sys.exit(1)


def display_message(title, message, priority=_PRIORITY_CRITICAL):
    """
    Displays a message on the user's desktop using libnotify-python.
    """
    message = pynotify.Notification(title, message)
    message.set_urgency(priority)
    message.show()


def check_orders(email, password, order_ids):
    """
    Gets the current status of your orders.
    """
    try:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        login(opener, email, password)
        try:
            for order_id in order_ids:
                show_order_status(opener, order_id)
        except:
            display_message(_NOTIFICATION_TITLE % order_id, 'Cannot check order status')
    except:
        display_message('Ticketmaster', 'Cannot log into Ticketmaster')


def login(opener, email, password):
    """
    Logs in to Ticketmaster using the given credentials.
    """
    # Request user authentication
    params = urllib.urlencode({'email': email, 'senha': password})
    response = opener.open('%s?tentaLogin=1' % _LOGIN_URI, params)

    # Invalid credentials check
    if response.read().find('senha incorreta') >= 0:
        raise Exception


def show_order_status(opener, order_id):
    """
    Shows the current status of your orders.
    """
    status_found = False

    # Request the order status page
    response = opener.open(_ORDER_URI % order_id)
    content = response.read()

    # Search for the order status codes
    for key, value in _STATUS_CODES.items():
        if content.find(key) >= 0:
            title = _NOTIFICATION_TITLE % order_id
            message = '%s. %s' % (value[0], _ORDERS_LINK)
            display_message(title, message, value[1])

            status_found = True
            break

    if not status_found:
        display_message(_NOTIFICATION_TITLE % order_id, 'Order status not found')


def main():
    """
    Main function.
    """
    p = optparse.OptionParser()

    # Required command line options
    p.add_option('--email'    , '-e', help='E-mail address used in your Ticketmaster credentials.')
    p.add_option('--password' , '-p', help='Password used in your Ticketmaster credentials.')
    p.add_option('--order-ids', '-o', help='Order IDs to be checked, separated by collons.')

    options = p.parse_args()[0]
    if not options.email or not options.password or not options.order_ids:
        p.print_help()
    else:
        # Parse the order ids
        order_ids = map(lambda s: s.strip(), options.order_ids.split(','))

        initialize_notification_system("Ticketmaster Order Status")
        check_orders(options.email, options.password, order_ids)


if __name__ == '__main__':
    main()
