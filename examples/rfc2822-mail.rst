MIME-Version: 1.0
In-Reply-To: <20100409150213.GA6303@iris.oostereind.endofinternet.org>
References: <20100409150213.GA6303@iris.oostereind.endofinternet.org>
Date: Fri, 9 Apr 2010 17:20:53 -0400
Message-ID: <i2t4335d2c41004091420oc9549f39t8535d0a266968387@mail.gmail.com>
Subject: Re: [Docutils-develop] nodes __cmp__
From: David Goodger <goodger@python.org>
To: Berend van Berkum <berend@dotmpe.com>
Cc: docutils-develop <docutils-develop@lists.sourceforge.net>

On Fri, Apr 9, 2010 at 11:02, Berend van Berkum <berend@dotmpe.com> wrote:
> I'm looking at testing some functionality and think I need a tree comparison.
> Looking at the nodes there is no implementation for cmp. Does someone here know if
> it has been tackled before?

Not that I know of.

> Also would anyone care to comment wether this would
> be a sane thing to have in nodes.py? I believe that could work out alright.

It could be useful. I'd recommend researching existing tree comparison
algorithms.

In the meantime, you could compare the repr() or the .pformat() of doctrees.

-- 
David Goodger <http://python.net/~goodger>


