"""seasonseat: seasonal seating fairness planner.

Plan seating across a season of events so that, over the whole season,
each attendee's cumulative seat quality is balanced, no one repeats a seat,
and adjacency (who sits next to whom) varies. Every plan carries an embedded
copy of its input so an independent command can re-derive and verify it.
"""

__version__ = "1.0.0"
__all__ = ["__version__"]