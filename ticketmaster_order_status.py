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


import urllib
import urllib2
import pynotify


# Base URL
_BASE_URL = 'https://ticketing.ticketmaster.com.br'

# Authentication and order status URIs
_LOGIN_URI = '%s/shwLogin.cfm' % _BASE_URL
_ORDER_URI = '%s/shwCompraDetalhe.cfm?pedidoID=%%s' % _BASE_URL

# Notification icons (based on GTK stock items)
_ICON_ERROR    = 'gtk-dialog-error'
_ICON_NEW      = 'gtk-add'
_ICON_WAITING  = 'gtk-refresh'
_ICON_BILLED   = 'gtk-dialog-info'
_ICON_REJECTED = 'gtk-stop'

# Notification messages to display according to the orders status
_TITLE = 'Ticketmaster Order %s'
_STATUS_CODES = {
    'Livre'      : ('Not processed yet.'     , _ICON_NEW),
    'StdReserva' : ('Reserving your tickets.', _ICON_WAITING),
    'StdCobranca': ('Charging your tickets.' , _ICON_WAITING),
    'VendaOk'    : ('Billed.'                , _ICON_BILLED),
    'Recusada'   : ('Rejected.'              , _ICON_REJECTED),
}


def initialize_notification_system(app_title):
    """
    Initializes the notification machinery. Change this if you want to use
    another notification system.
    """
    if not pynotify.init(app_title):
        import sys
        sys.exit(1)


def display_message(title, message, icon=_ICON_ERROR):
    """
    Displays a message on the user's desktop using libnotify-python. Change
    this if you want to use another notification system.
    """
    pynotify.Notification(title, message, icon).show()


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
            display_message(_TITLE % order_id, 'Cannot check status.')
    except:
        display_message('Ticketmaster', 'Login failed.')


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
    # Request the order status page
    response = opener.open(_ORDER_URI % order_id)
    content = response.read()

    # Search for the order status codes
    for key, value in _STATUS_CODES.items():
        if content.find(key) >= 0:
            display_message(_TITLE % order_id, value[0], value[1])
            break
    else:
        display_message(_TITLE % order_id, 'Status not found.')


def main():
    """
    Main function.
    """
    initialize_notification_system("Ticketmaster Order Status")

    import optparse
    p = optparse.OptionParser()

    # Required command line options
    p.add_option('--email'    , '-e',
        help='E-mail address used in your Ticketmaster credentials.')
    p.add_option('--password' , '-p',
        help='Password used in your Ticketmaster credentials.')
    p.add_option('--order-ids', '-o',
        help='Order IDs to be checked, separated by collons.')

    options = p.parse_args()[0]
    if not options.email or not options.password or not options.order_ids:
        p.print_help()
    else:
        order_ids = map(lambda s: s.strip(), options.order_ids.split(','))
        check_orders(options.email, options.password, order_ids)


if __name__ == '__main__':
    main()
