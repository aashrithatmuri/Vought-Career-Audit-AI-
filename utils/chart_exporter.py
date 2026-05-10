import matplotlib.pyplot as plt


def save_chart(
    figure,
    filename
):
    figure.savefig(
        filename,
        bbox_inches="tight"
    )

    return filename