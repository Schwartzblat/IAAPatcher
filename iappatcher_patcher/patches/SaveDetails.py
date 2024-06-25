import re
from iappatcher_patcher.patches.Patch import Patch


class SaveDetails(Patch):
    SET_SKU_DETAILS = re.compile(
        '.method public.*<init>\(L.*;ILjava/lang/String;Ljava/lang/String;L.*;Landroid/os/Bundle;\)V\s.*\n')

    FIELD_RE = re.compile('\.field .*;\n')

    FIELD_NAME = 'product_id'

    GLOBAL_STATIC_FIELD = f"""
    .field public static {FIELD_NAME}:Ljava/lang/String;
    """

    CLASSPATH_RE = re.compile('\.class public.*(L.*);')

    def __init__(self, extracted_path):
        super().__init__(extracted_path)
        self.print_message = "[+] Patching the set sku details method..."

    def class_filter(self, class_data: str) -> bool:
        if self.SET_SKU_DETAILS.search(class_data) is not None:
            return True
        return False

    def class_modifier(self, class_data, patches_globals: dict) -> str:
        classpath = self.CLASSPATH_RE.findall(class_data)[0]
        patches_globals['DETAILS_CLASSPATH'] = classpath
        field_body = self.FIELD_RE.findall(class_data)[0]

        new_class_data = class_data.replace(
            field_body,
            f'{field_body}\n\t{self.GLOBAL_STATIC_FIELD}',
            1
        )

        set_sku_details = self.SET_SKU_DETAILS.findall(class_data)[0]

        new_set_sku_details = set_sku_details + f"""
        sput-object p3, {classpath};->{self.FIELD_NAME}:Ljava/lang/String;
        """

        return new_class_data.replace(
            set_sku_details,
            new_set_sku_details,
        )
