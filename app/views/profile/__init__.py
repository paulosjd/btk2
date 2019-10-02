from .bookmarks.bookmarks_add import AddBookmarksView
from .bookmarks.bookmarks_edit import EditBookmarksView
from .custom_metric_add import CustomMetricAdd
from .info_update import ProfileInfoUpdate
from .menu_item_add import MenuItemAdd
from .param_colors_update import ParamColorsUpdateView
from .summary_data import ProfileSummaryData
from .target_update import TargetUpdateView

__all__ = [
    AddBookmarksView,
    CustomMetricAdd,
    EditBookmarksView,
    MenuItemAdd,
    ParamColorsUpdateView,
    ProfileInfoUpdate,
    ProfileSummaryData,
    TargetUpdateView,
]
