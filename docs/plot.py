# dependencies
import azely
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter


def plot_one_liner() -> None:
    """Plot an example of one-liner."""
    fig, ax = plt.subplots(figsize=(12, 4))

    azely.calc("Sun", "Tokyo", "2025-07-07", source=None).el.plot(
        ylabel="Elevation (deg)",
        ylim=(0, 90),
        grid=True,
    )

    fig.tight_layout()
    fig.savefig("docs/_static/one-liner.svg")


def plot_multiple_objects() -> None:
    """Plot an example of multiple objects."""
    fig, ax = plt.subplots(figsize=(12, 4))

    for obj in ("Sun", "Sgr A*", "M87", "M104", "Cen A"):
        df = azely.calc(obj, "ALMA AOS", "2017 April 11 UTC", source=None)
        df.el.plot(ax=ax, label=df.object.name)

    ax.set_title(f"Location: {df.location.name}")
    ax.set_ylabel("Elevation (deg)")
    ax.set_ylim(0, 90)
    ax.grid(which="both")
    ax.legend()

    fig.tight_layout()
    fig.savefig("docs/_static/multiple-objects.svg")


def plot_lst_axis() -> None:
    """Plot an example of lst axis."""
    fig, ax_jst = plt.subplots(figsize=(12, 4))
    ax_lst = ax_jst.twiny()

    for obj in ("M78", "M87"):
        df = azely.calc(obj, "Tokyo", "2025-07-07", source=None)
        df.el.plot(ax=ax_jst, label=df.object.name)

    ax_jst.set_title(f"Location: {df.location.name}")
    ax_jst.set_ylabel("Elevation (deg)")
    ax_jst.set_ylim(0, 90)
    ax_jst.grid(which="both")
    ax_jst.legend()
    ax_jst.margins(0)

    # plot invisible elevation for the LST axis
    df.in_lst().el.plot(ax=ax_lst, alpha=0)
    ax_lst.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    ax_lst.margins(0)

    fig.tight_layout()
    fig.autofmt_xdate(rotation=0)
    fig.savefig("docs/_static/lst-axis.svg")


if __name__ == "__main__":
    plot_one_liner()
    plot_multiple_objects()
    plot_lst_axis()
