// Generated from: e2e/features/health_check.feature
import { test } from "playwright-bdd";

test.describe('システムのE2E疎通確認', () => {

  test('トップページでAPI経由のメッセージを確認できる', async ({ Given, When, Then, And, page }) => { 
    await Given('Kvellのデータベースが正常に起動している'); 
    await And('データベースにシステムメッセージ "Hello Kvell" が登録されている'); 
    await When('ユーザーがKvellのトップページにアクセスする', null, { page }); 
    await And('ヘルスチェックボタンをクリックする', null, { page }); 
    await Then('画面上にシステムメッセージ "Hello Kvell" が表示される', null, { page }); 
  });

});

// == technical section ==

test.use({
  $test: [({}, use) => use(test), { scope: 'test', box: true }],
  $uri: [({}, use) => use('e2e/features/health_check.feature'), { scope: 'test', box: true }],
  $bddFileData: [({}, use) => use(bddFileData), { scope: "test", box: true }],
});

const bddFileData = [ // bdd-data-start
  {"pwTestLine":6,"pickleLine":5,"tags":[],"steps":[{"pwStepLine":7,"gherkinStepLine":6,"keywordType":"Context","textWithKeyword":"Given Kvellのデータベースが正常に起動している","stepMatchArguments":[]},{"pwStepLine":8,"gherkinStepLine":7,"keywordType":"Context","textWithKeyword":"And データベースにシステムメッセージ \"Hello Kvell\" が登録されている","stepMatchArguments":[{"group":{"start":17,"value":"\"Hello Kvell\"","children":[{"start":18,"value":"Hello Kvell","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":9,"gherkinStepLine":8,"keywordType":"Action","textWithKeyword":"When ユーザーがKvellのトップページにアクセスする","stepMatchArguments":[]},{"pwStepLine":10,"gherkinStepLine":9,"keywordType":"Action","textWithKeyword":"And ヘルスチェックボタンをクリックする","stepMatchArguments":[]},{"pwStepLine":11,"gherkinStepLine":10,"keywordType":"Outcome","textWithKeyword":"Then 画面上にシステムメッセージ \"Hello Kvell\" が表示される","stepMatchArguments":[{"group":{"start":14,"value":"\"Hello Kvell\"","children":[{"start":15,"value":"Hello Kvell","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]}]},
]; // bdd-data-end