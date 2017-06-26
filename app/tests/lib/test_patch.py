"""
@AUTHOR: meyersbs
"""

from unittest import TestCase
from app.tests.testfiles import *

from app.lib.patch import *


class PatchTestCase(TestCase):
    def setUp(self):
        pass

    def test_chunks(self):
        with open(DIFF_4001_5001_PATH, 'r') as f:
            patch_text = f.read()

        p = Patch(patch_text)

        # Sub-Test 1
        self.assertEqual(60, len(p.get_lines()))

        # Sub-Test 2
        chunks = p.get_chunks()
        self.assertEqual(5, len(chunks))

        # Sub-Test 3
        expected = {
                5: " #include \"chrome/browser/ui/toolbar/action_box_button_controller.h\"",
                6: " ",
                7: " #include \"base/logging.h\"",
                8: "+#include \"base/metrics/histogram.h\"",
                9: " #include \"base/utf_string_conversions.h\"",
                10: " #include \"chrome/browser/extensions/extension_service.h\"",
                11: " #include \"chrome/browser/extensions/extension_system.h\""
            }
        self.assertDictEqual(expected, chunks[0].get_lines())

        # Sub-Test 4
        expected = {
                21: " #include \"chrome/common/extensions/extension_set.h\"",
                22: " #include \"content/public/browser/notification_service.h\"",
                23: " #include \"content/public/browser/notification_source.h\"",
                24: "+#include \"content/public/browser/user_metrics.h\"",
                25: " #include \"content/public/browser/web_contents.h\"",
                26: " #include \"content/public/browser/web_intents_dispatcher.h\"",
                27: " #include \"grit/generated_resources.h\""
            }
        self.assertDictEqual(expected, chunks[1].get_lines())

        # Sub-Test 5
        expected = {
                48: " ",
                49: " }  // namespace",
                50: " ",
                51: "+using content::UserMetricsAction;",
                52: "+",
                53: " ActionBoxButtonController::ActionBoxButtonController(Browser* browser,",
                54: "                                                      Delegate* delegate)",
                55: "     : browser_(browser),",
                56: "       delegate_(delegate),",
                57: "-      next_extension_command_id_(EXTENSION_COMMAND_FIRST) {",
                58: "+      next_extension_command_id_(EXTENSION_COMMAND_FIRST),",
                59: "+      should_send_uma_(true) {",
                60: "   DCHECK(browser_);",
                61: "   DCHECK(delegate_);",
                62: "   registrar_.Add(this,"
            }
        self.assertDictEqual(expected, chunks[2].get_lines())

        # Sub-Test 6
        expected = {
                105: "     // Add link to the Web Store to find additional share intents.",
                106: "     menu_model->AddItemWithStringId(CWS_FIND_SHARE_INTENTS_COMMAND,",
                107: "         IDS_FIND_SHARE_INTENTS);",
                108: "+",
                109: "+    content::RecordAction(UserMetricsAction(\"ActionBox.ClickButton\"));",
                110: "+    if (should_send_uma_) {",
                111: "+      UMA_HISTOGRAM_ENUMERATION(\"ActionBox.ShareCommandCount\",",
                112: "+          next_share_intent_command_id - SHARE_COMMAND_FIRST,",
                113: "+          SHARE_COMMAND_LAST);",
                114: "+      should_send_uma_ = false;",
                115: "+    }",
                116: "   }",
                117: " ",
                118: "   // Add Extensions."
            }
        self.assertDictEqual(expected, chunks[3].get_lines())

        # Sub-Test 7
        expected = {
                238: "                                 content::PAGE_TRANSITION_LINK);",
                239: "   params.disposition = NEW_FOREGROUND_TAB;",
                240: "   chrome::Navigate(&params);",
                241: "+",
                242: "+  content::RecordAction(UserMetricsAction(\"ActionBox.FindShares\"));",
                243: "+  should_send_uma_ = true;",
                244: " }"
            }
        self.assertDictEqual(expected, chunks[4].get_lines())

        # Sub-Test 8
        expected = [
                [5, 6, 5, 7], [20, 6, 21, 7], [46, 11, 48, 14],
                [100, 6, 105, 14], [225, 4, 238, 7]
            ]
        actual = p.get_hunks()
        self.assertListEqual(expected, actual)

        # Sub-Test 9
        expected = {
                105: "     // Add link to the Web Store to find additional share intents.",
                106: "     menu_model->AddItemWithStringId(CWS_FIND_SHARE_INTENTS_COMMAND,",
                107: "         IDS_FIND_SHARE_INTENTS);",
                108: "+",
                109: "+    content::RecordAction(UserMetricsAction(\"ActionBox.ClickButton\"));",
                110: "+    if (should_send_uma_) {",
                111: "+      UMA_HISTOGRAM_ENUMERATION(\"ActionBox.ShareCommandCount\",",
                112: "+          next_share_intent_command_id - SHARE_COMMAND_FIRST,",
                113: "+          SHARE_COMMAND_LAST);",
                114: "+      should_send_uma_ = false;",
                115: "+    }",
                116: "   }",
                117: " ",
                118: "   // Add Extensions."
            }
        actual = p.get_chunk_by_line(113).get_lines()
        self.assertDictEqual(expected, actual)

        # Sub-Test 10
        expected = [100, 6, 105, 14]
        actual = p.get_chunk_by_line(113).get_hunk()
        self.assertListEqual(expected, actual)
