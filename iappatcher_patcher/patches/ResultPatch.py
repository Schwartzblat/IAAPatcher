import re
from iappatcher_patcher.patches.Patch import Patch
from iappatcher_patcher.patches.SaveDetails import SaveDetails


class ResultPatch(Patch):
    ON_ACTIVITY_RESULT_RE = re.compile(
        "\.method.*onActivityResult\(IILandroid/content/Intent;\)V\s+.*\n"
    )

    NEW_ON_ACTIVITY_RESULT = """
    .param p3, "intent"
    
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    move-object p3, v0

    new-instance v0, Landroid/os/Bundle;

    invoke-direct {v0}, Landroid/os/Bundle;-><init>()V

    .local v0, "extras":Landroid/os/Bundle;
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    .local v1, "sb":Ljava/lang/StringBuilder;
    const-string v2, "{\'orderId\':\'12999763169054705758.1371079406387615\', \'packageName\':\'{{PACKAGE_NAME}}\', \'productId\':\'"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    sget-object v2, {{CLASSPATH}};->product_id:Ljava/lang/String;

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "\', \'purchaseTime\':1345678900000, \'purchaseToken\' : \'122333444455555\', \'developerPayload\':\'\'}"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "RESPONSE_CODE"

    const/4 v3, 0x0

    invoke-virtual {v0, v2, v3}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V

    const-string v2, "INAPP_PURCHASE_DATA"

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v0, v2, v3}, Landroid/os/Bundle;->putString(Ljava/lang/String;Ljava/lang/String;)V

    const-string v2, "INAPP_DATA_SIGNATURE"

    const-string v3, ""

    invoke-virtual {v0, v2, v3}, Landroid/os/Bundle;->putString(Ljava/lang/String;Ljava/lang/String;)V

    invoke-virtual {p3, v0}, Landroid/content/Intent;->putExtras(Landroid/os/Bundle;)Landroid/content/Intent;
    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path)
        self.print_message = "[+] Patching the save onActivityResult method..."
        self.dependencies = [SaveDetails]

    def class_filter(self, class_data: str) -> bool:
        if "\"Got onActivityResult with wrong requestCode: \"" in class_data:
            return True
        return False

    def class_modifier(self, class_data, patches_globals: dict) -> str:
        on_activity_result = self.ON_ACTIVITY_RESULT_RE.findall(class_data)[0]
        result_setup = self.NEW_ON_ACTIVITY_RESULT.replace('{{CLASSPATH}}', patches_globals.get('DETAILS_CLASSPATH'))
        apk_details = patches_globals.get('apk_details')
        new_on_activity_result = on_activity_result + result_setup.replace('{{PACKAGE_NAME}}', apk_details.package)

        return class_data.replace(
            on_activity_result,
            new_on_activity_result,
        )
