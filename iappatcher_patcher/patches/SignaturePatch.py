import re
from iappatcher_patcher.patches.Patch import Patch


class SignaturePatch(Patch):
    SIGNATURE_FUNCTION_RE = re.compile(
        '\.method public static \w+\(Ljava/lang/String;Ljava/lang/String;\)Z\s+[^\n]+\n(.*?)\.end method', re.DOTALL)

    def __init__(self, extracted_path):
        super().__init__(extracted_path)
        self.print_message = "[+] Patching the purchase signature verifier method..."

    def class_filter(self, class_data: str) -> bool:
        if "\"Error generating PublicKey from encoded key: \"" in class_data:
            return True
        return False

    def class_modifier(self, class_data, patches_globals: dict) -> str:
        signature_function = self.SIGNATURE_FUNCTION_RE.findall(class_data)[0]
        return class_data.replace(
            signature_function,
            """
                const/4 v0, 0x1
                
                return v0
            """,
        )
