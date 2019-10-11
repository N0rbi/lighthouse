import seaborn.utils as utils
import seaborn as sns
import matplotlib as mpl
import seaborn.rcmod as rcmod
from core.utils.Singleton import Singleton


class TrackFontScale(metaclass=Singleton):
    font_scale = -1
    def __init__(self):
        rcmod.plotting_context = self.save_font_size(rcmod.plotting_context)

    def save_font_size(self, func):
        def _decorator(*args, **kwargs):
            self.font_scale = kwargs['font_scale'] if kwargs is not None and 'font_scale' in kwargs else args[1]
            return func(*args, **kwargs)
        return _decorator


TrackFontScale()


class CustomFacetGrid(sns.FacetGrid):
    """
    Multi-plot grid for plotting conditional relationships.

    Support for labeling on top of the grid
    """

    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)

    def add_legend(self, legend_data=None, title=None, label_order=None,
                   legend_placement="right", no_title=False,
                   **kwargs):
        """Draw a legend, maybe placing it outside axes and resizing the figure.

        Parameters
        ----------
        legend_data : dict, optional
            Dictionary mapping label names to matplotlib artist handles. The
            default reads from ``self._legend_data``.
        title : string, optional
            Title for the legend. The default reads from ``self._hue_var``.
        label_order : list of labels, optional
            The order that the legend entries should appear in. The default
            reads from ``self.hue_names``.
        kwargs : key, value pairings
            Other keyword arguments are passed to the underlying legend methods
            on the Figure or Axes object.

        Returns
        -------
        self : Grid instance
            Returns self for easy chaining.

        """
        # Find the data for the legend
        legend_data = self._legend_data if legend_data is None else legend_data
        if label_order is None:
            if self.hue_names is None:
                label_order = list(legend_data.keys())
            else:
                label_order = list(map(utils.to_utf8, self.hue_names))

        blank_handle = mpl.patches.Patch(alpha=0, linewidth=0)
        handles = [legend_data.get(l, blank_handle) for l in label_order]
        title = self._hue_var if title is None else title
        try:
            title_size = mpl.rcParams["axes.labelsize"] * .85
        except TypeError:  # labelsize is something like "large"
            title_size = mpl.rcParams["axes.labelsize"]

        # Set default legend kwargs
        kwargs.setdefault("scatterpoints", 1)

        if self._legend_out:
            if legend_placement == "right":
                kwargs.setdefault("frameon", False)

                # Draw a full-figure legend outside the grid
                figlegend = self.fig.legend(handles, label_order, "center right",
                                            **kwargs)
                self._legend = figlegend
                if not no_title:
                    figlegend.set_title(title, prop={"size": title_size})

                # Draw the plot to set the bounding boxes correctly
                if hasattr(self.fig.canvas, "get_renderer"):
                    self.fig.draw(self.fig.canvas.get_renderer())

                # Calculate and set the new width of the figure so the legend fits
                legend_width = figlegend.get_window_extent().width / self.fig.dpi
                fig_width, fig_height = self.fig.get_size_inches()
                self.fig.set_size_inches(fig_width + legend_width, fig_height)

                # Draw the plot again to get the new transformations
                if hasattr(self.fig.canvas, "get_renderer"):
                    self.fig.draw(self.fig.canvas.get_renderer())

                # Now calculate how much space we need on the right side
                legend_width = figlegend.get_window_extent().width / self.fig.dpi
                space_needed = legend_width / (fig_width + legend_width)
                margin = .04 if self._margin_titles else .01
                self._space_needed = margin + space_needed
                right = 1 - self._space_needed

                # Place the subplot axes to give space for the legend
                self.fig.subplots_adjust(right=right)
            elif legend_placement == "top":
                kwargs.setdefault("frameon", False)

                # Draw a full-figure legend outside the grid
                figlegend = self.fig.legend(handles, label_order, "upper center", ncol=len(handles),
                                            **kwargs)
                self._legend = figlegend
                if not no_title:
                    figlegend.set_title(title, prop={"size": title_size})

                # Draw the plot to set the bounding boxes correctly
                if hasattr(self.fig.canvas, "get_renderer"):
                    self.fig.draw(self.fig.canvas.get_renderer())

                # Calculate and set the new width of the figure so the legend fits
                # legend_width = figlegend.get_window_extent().width / self.fig.dpi
                # fig_width, fig_height = self.fig.get_size_inches()
                # self.fig.set_size_inches(fig_width + legend_width, fig_height)

                legend_height = figlegend.get_window_extent().height / self.fig.dpi
                fig_width, fig_height = self.fig.get_size_inches()
                self.fig.set_size_inches(fig_width, fig_height + legend_height)

                # Draw the plot again to get the new transformations
                if hasattr(self.fig.canvas, "get_renderer"):
                    self.fig.draw(self.fig.canvas.get_renderer())

                # Now calculate how much space we need on the right side
                legend_height = figlegend.get_window_extent().height / self.fig.dpi
                space_needed = legend_height / (fig_height + legend_height)
                margin = .04 * TrackFontScale().font_scale
                self._space_needed = margin + space_needed
                top = 1 - self._space_needed

                # Place the subplot axes to give space for the legend
                self.fig.subplots_adjust(top=top)
        else:
            # Draw a legend in the first axis
            ax = self.axes.flat[0]
            leg = ax.legend(handles, label_order, loc="best", **kwargs)
            if not no_title:
                leg.set_title(title, prop={"size": title_size})

        return self