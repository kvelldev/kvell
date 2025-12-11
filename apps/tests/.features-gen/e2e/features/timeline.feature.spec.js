// Generated from: e2e/features/timeline.feature
import { test } from "playwright-bdd";

test.describe('Timeline', () => {

  test.beforeEach('Background: System Configuration', async ({ Given, And }, testInfo) => { if (testInfo.error) return;
    await Given('システムの "Decay time" は "1分" に設定されている'); 
    await And('システムの "冷却閾値（Hot/Ashの境界）" は "Decay timeの30%" に設定されている'); 
  });
  
  test.describe('Timelineは「常に最新」を表示することをデフォルトとする', () => {

    test.beforeEach('Background', async ({ Given }, testInfo) => { if (testInfo.error) return;
      await Given('複数の "Spark" が存在し、"Timeline" が画面高さを超えている'); 
    });
    
    test('初期表示時の挙動 (Default Sticky)', async ({ When, Then, And, page }) => { 
      await When('ユーザーがページを開く（またはリロードする）', null, { page }); 
      await Then('"Timeline" は最初から「最下部」にスクロールされた状態で表示される', null, { page }); 
      await And('ユーザーが操作しなくても、新しい "Spark" が来れば自動で表示される', null, { page }); 
    });

    test('ユーザーが過去ログを見ている場合 (Scroll Up)', async ({ When, Then, page }) => { 
      await When('ユーザーが意図的に上へスクロールする', null, { page }); 
      await Then('自動スクロールは解除され、その場に留まる（新しいSparkが来ても勝手に動かない）', null, { page }); 
    });

  });

  test.describe('Sparkは「熱量」と「残り時間」を可視化する', () => {

    test.beforeEach('Background', async ({ Given, page }, testInfo) => { if (testInfo.error) return;
      await Given('ユーザーは "Timeline" を閲覧している', null, { page }); 
    });
    
    test('発生直後のSpark（高温状態）', async ({ When, Then, And, page }) => { 
      await When('新しい "Spark" が投稿される（残り寿命 100%〜30%）', null, { page }); 
      await Then('その "Spark" は「白文字（Smoke White）」で表示される', null, { page }); 
      await And('その "Spark" は「オレンジ色の枠線（Ember Border）」と「発光（Glow）」を持つ', null, { page }); 
      await And('その "Spark" には「残り時間（例: 09:59）」がカウントダウン表示される', null, { page }); 
    });

    test('冷却されたSpark（灰化状態）', async ({ Given, When, Then, And, page }) => { 
      await Given('投稿から時間が経過している "Spark" がある'); 
      await When('その "Spark" の残り寿命が "冷却閾値" を下回る', null, { page }); 
      await Then('その "Spark" は「灰色文字（Ash Gray）」へと変化する', null, { page }); 
      await And('その "Spark" の「枠線」と「発光」は消失する（border-0 / shadow-none）', null, { page }); 
      await And('「残り時間」の表示も灰色になり、カウントダウンは継続する', null, { page }); 
    });

  });

  test.describe('Sparkが一つもない場合は「静寂」を表現する', () => {

    test.beforeEach('Background', async ({ Given }, testInfo) => { if (testInfo.error) return;
      await Given('"Timeline" に表示できる有効な "Spark" が0件である'); 
    });
    
    test('Empty Stateの表示 (The Silent Sky)', async ({ Then, And, page }) => { 
      await Then('画面中央にアイコン等は表示せず、テキストのみを表示する', null, { page }); 
      await And('テキストの内容は「静かな夜空です。」とする', null, { page }); 
    });

  });

});

// == technical section ==

test.afterEach('AfterEach Hooks', ({ $runScenarioHooks }) => $runScenarioHooks('after', {  }));

test.use({
  $test: [({}, use) => use(test), { scope: 'test', box: true }],
  $uri: [({}, use) => use('e2e/features/timeline.feature'), { scope: 'test', box: true }],
  $bddFileData: [({}, use) => use(bddFileData), { scope: "test", box: true }],
});

const bddFileData = [ // bdd-data-start
  {"pwTestLine":17,"pickleLine":14,"tags":[],"steps":[{"pwStepLine":7,"gherkinStepLine":7,"keywordType":"Context","textWithKeyword":"Given システムの \"Decay time\" は \"1分\" に設定されている","isBg":true,"stepMatchArguments":[{"group":{"start":6,"value":"\"Decay time\"","children":[{"start":7,"value":"Decay time","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":21,"value":"\"1分\"","children":[{"start":22,"value":"1分","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":8,"gherkinStepLine":8,"keywordType":"Context","textWithKeyword":"And システムの \"冷却閾値（Hot/Ashの境界）\" は \"Decay timeの30%\" に設定されている","isBg":true,"stepMatchArguments":[{"group":{"start":6,"value":"\"冷却閾値（Hot/Ashの境界）\"","children":[{"start":7,"value":"冷却閾値（Hot/Ashの境界）","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":27,"value":"\"Decay timeの30%\"","children":[{"start":28,"value":"Decay timeの30%","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":14,"gherkinStepLine":12,"keywordType":"Context","textWithKeyword":"Given 複数の \"Spark\" が存在し、\"Timeline\" が画面高さを超えている","isBg":true,"stepMatchArguments":[{"group":{"start":4,"value":"\"Spark\"","children":[{"start":5,"value":"Spark","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":17,"value":"\"Timeline\"","children":[{"start":18,"value":"Timeline","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":18,"gherkinStepLine":15,"keywordType":"Action","textWithKeyword":"When ユーザーがページを開く（またはリロードする）","stepMatchArguments":[]},{"pwStepLine":19,"gherkinStepLine":16,"keywordType":"Outcome","textWithKeyword":"Then \"Timeline\" は最初から「最下部」にスクロールされた状態で表示される","stepMatchArguments":[{"group":{"start":0,"value":"\"Timeline\"","children":[{"start":1,"value":"Timeline","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":20,"gherkinStepLine":17,"keywordType":"Outcome","textWithKeyword":"And ユーザーが操作しなくても、新しい \"Spark\" が来れば自動で表示される","stepMatchArguments":[{"group":{"start":17,"value":"\"Spark\"","children":[{"start":18,"value":"Spark","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]}]},
  {"pwTestLine":23,"pickleLine":19,"tags":[],"steps":[{"pwStepLine":7,"gherkinStepLine":7,"keywordType":"Context","textWithKeyword":"Given システムの \"Decay time\" は \"1分\" に設定されている","isBg":true,"stepMatchArguments":[{"group":{"start":6,"value":"\"Decay time\"","children":[{"start":7,"value":"Decay time","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":21,"value":"\"1分\"","children":[{"start":22,"value":"1分","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":8,"gherkinStepLine":8,"keywordType":"Context","textWithKeyword":"And システムの \"冷却閾値（Hot/Ashの境界）\" は \"Decay timeの30%\" に設定されている","isBg":true,"stepMatchArguments":[{"group":{"start":6,"value":"\"冷却閾値（Hot/Ashの境界）\"","children":[{"start":7,"value":"冷却閾値（Hot/Ashの境界）","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":27,"value":"\"Decay timeの30%\"","children":[{"start":28,"value":"Decay timeの30%","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":14,"gherkinStepLine":12,"keywordType":"Context","textWithKeyword":"Given 複数の \"Spark\" が存在し、\"Timeline\" が画面高さを超えている","isBg":true,"stepMatchArguments":[{"group":{"start":4,"value":"\"Spark\"","children":[{"start":5,"value":"Spark","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":17,"value":"\"Timeline\"","children":[{"start":18,"value":"Timeline","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":24,"gherkinStepLine":20,"keywordType":"Action","textWithKeyword":"When ユーザーが意図的に上へスクロールする","stepMatchArguments":[]},{"pwStepLine":25,"gherkinStepLine":21,"keywordType":"Outcome","textWithKeyword":"Then 自動スクロールは解除され、その場に留まる（新しいSparkが来ても勝手に動かない）","stepMatchArguments":[]}]},
  {"pwTestLine":36,"pickleLine":27,"tags":[],"steps":[{"pwStepLine":7,"gherkinStepLine":7,"keywordType":"Context","textWithKeyword":"Given システムの \"Decay time\" は \"1分\" に設定されている","isBg":true,"stepMatchArguments":[{"group":{"start":6,"value":"\"Decay time\"","children":[{"start":7,"value":"Decay time","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":21,"value":"\"1分\"","children":[{"start":22,"value":"1分","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":8,"gherkinStepLine":8,"keywordType":"Context","textWithKeyword":"And システムの \"冷却閾値（Hot/Ashの境界）\" は \"Decay timeの30%\" に設定されている","isBg":true,"stepMatchArguments":[{"group":{"start":6,"value":"\"冷却閾値（Hot/Ashの境界）\"","children":[{"start":7,"value":"冷却閾値（Hot/Ashの境界）","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":27,"value":"\"Decay timeの30%\"","children":[{"start":28,"value":"Decay timeの30%","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":33,"gherkinStepLine":25,"keywordType":"Context","textWithKeyword":"Given ユーザーは \"Timeline\" を閲覧している","isBg":true,"stepMatchArguments":[{"group":{"start":6,"value":"\"Timeline\"","children":[{"start":7,"value":"Timeline","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":37,"gherkinStepLine":28,"keywordType":"Action","textWithKeyword":"When 新しい \"Spark\" が投稿される（残り寿命 100%〜30%）","stepMatchArguments":[{"group":{"start":4,"value":"\"Spark\"","children":[{"start":5,"value":"Spark","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":38,"gherkinStepLine":29,"keywordType":"Outcome","textWithKeyword":"Then その \"Spark\" は「白文字（Smoke White）」で表示される","stepMatchArguments":[{"group":{"start":3,"value":"\"Spark\"","children":[{"start":4,"value":"Spark","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":39,"gherkinStepLine":30,"keywordType":"Outcome","textWithKeyword":"And その \"Spark\" は「オレンジ色の枠線（Ember Border）」と「発光（Glow）」を持つ","stepMatchArguments":[{"group":{"start":3,"value":"\"Spark\"","children":[{"start":4,"value":"Spark","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":40,"gherkinStepLine":31,"keywordType":"Outcome","textWithKeyword":"And その \"Spark\" には「残り時間（例: 09:59）」がカウントダウン表示される","stepMatchArguments":[{"group":{"start":3,"value":"\"Spark\"","children":[{"start":4,"value":"Spark","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]}]},
  {"pwTestLine":43,"pickleLine":33,"tags":[],"steps":[{"pwStepLine":7,"gherkinStepLine":7,"keywordType":"Context","textWithKeyword":"Given システムの \"Decay time\" は \"1分\" に設定されている","isBg":true,"stepMatchArguments":[{"group":{"start":6,"value":"\"Decay time\"","children":[{"start":7,"value":"Decay time","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":21,"value":"\"1分\"","children":[{"start":22,"value":"1分","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":8,"gherkinStepLine":8,"keywordType":"Context","textWithKeyword":"And システムの \"冷却閾値（Hot/Ashの境界）\" は \"Decay timeの30%\" に設定されている","isBg":true,"stepMatchArguments":[{"group":{"start":6,"value":"\"冷却閾値（Hot/Ashの境界）\"","children":[{"start":7,"value":"冷却閾値（Hot/Ashの境界）","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":27,"value":"\"Decay timeの30%\"","children":[{"start":28,"value":"Decay timeの30%","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":33,"gherkinStepLine":25,"keywordType":"Context","textWithKeyword":"Given ユーザーは \"Timeline\" を閲覧している","isBg":true,"stepMatchArguments":[{"group":{"start":6,"value":"\"Timeline\"","children":[{"start":7,"value":"Timeline","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":44,"gherkinStepLine":34,"keywordType":"Context","textWithKeyword":"Given 投稿から時間が経過している \"Spark\" がある","stepMatchArguments":[{"group":{"start":14,"value":"\"Spark\"","children":[{"start":15,"value":"Spark","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":45,"gherkinStepLine":35,"keywordType":"Action","textWithKeyword":"When その \"Spark\" の残り寿命が \"冷却閾値\" を下回る","stepMatchArguments":[{"group":{"start":3,"value":"\"Spark\"","children":[{"start":4,"value":"Spark","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":18,"value":"\"冷却閾値\"","children":[{"start":19,"value":"冷却閾値","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":46,"gherkinStepLine":36,"keywordType":"Outcome","textWithKeyword":"Then その \"Spark\" は「灰色文字（Ash Gray）」へと変化する","stepMatchArguments":[{"group":{"start":3,"value":"\"Spark\"","children":[{"start":4,"value":"Spark","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":47,"gherkinStepLine":37,"keywordType":"Outcome","textWithKeyword":"And その \"Spark\" の「枠線」と「発光」は消失する（border-0 / shadow-none）","stepMatchArguments":[{"group":{"start":3,"value":"\"Spark\"","children":[{"start":4,"value":"Spark","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":48,"gherkinStepLine":38,"keywordType":"Outcome","textWithKeyword":"And 「残り時間」の表示も灰色になり、カウントダウンは継続する","stepMatchArguments":[]}]},
  {"pwTestLine":59,"pickleLine":52,"tags":[],"steps":[{"pwStepLine":7,"gherkinStepLine":7,"keywordType":"Context","textWithKeyword":"Given システムの \"Decay time\" は \"1分\" に設定されている","isBg":true,"stepMatchArguments":[{"group":{"start":6,"value":"\"Decay time\"","children":[{"start":7,"value":"Decay time","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":21,"value":"\"1分\"","children":[{"start":22,"value":"1分","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":8,"gherkinStepLine":8,"keywordType":"Context","textWithKeyword":"And システムの \"冷却閾値（Hot/Ashの境界）\" は \"Decay timeの30%\" に設定されている","isBg":true,"stepMatchArguments":[{"group":{"start":6,"value":"\"冷却閾値（Hot/Ashの境界）\"","children":[{"start":7,"value":"冷却閾値（Hot/Ashの境界）","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":27,"value":"\"Decay timeの30%\"","children":[{"start":28,"value":"Decay timeの30%","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":56,"gherkinStepLine":50,"keywordType":"Context","textWithKeyword":"Given \"Timeline\" に表示できる有効な \"Spark\" が0件である","isBg":true,"stepMatchArguments":[{"group":{"start":0,"value":"\"Timeline\"","children":[{"start":1,"value":"Timeline","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"},{"group":{"start":21,"value":"\"Spark\"","children":[{"start":22,"value":"Spark","children":[{"children":[]}]},{"children":[{"children":[]}]}]},"parameterTypeName":"string"}]},{"pwStepLine":60,"gherkinStepLine":53,"keywordType":"Outcome","textWithKeyword":"Then 画面中央にアイコン等は表示せず、テキストのみを表示する","stepMatchArguments":[]},{"pwStepLine":61,"gherkinStepLine":54,"keywordType":"Outcome","textWithKeyword":"And テキストの内容は「静かな夜空です。」とする","stepMatchArguments":[]}]},
]; // bdd-data-end