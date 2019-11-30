from .bookmarks.bookmarks_add import AddBookmarksView
from .bookmarks.bookmarks_edit import EditBookmarksView
from .custom_metric_add import CustomMetricAdd
from .info_update import ProfileInfoUpdate
from .linked_param_crud import LinkedParamCrud
from .menu_item_add import MenuItemAdd
from .param_colors_update import ParamColorsUpdateView
from .profile_report_view import ProfileReportView
from .profile_share_menu import ProfileShareMenu
from .summary_data import ProfileSummaryData
from .target_update import TargetUpdateView

__all__ = [
    AddBookmarksView,
    CustomMetricAdd,
    EditBookmarksView,
    LinkedParamCrud,
    MenuItemAdd,
    ParamColorsUpdateView,
    ProfileInfoUpdate,
    ProfileReportView,
    ProfileShareMenu,
    ProfileSummaryData,
    TargetUpdateView,
]
