/**
 * About Page (Smart Component)
 * 法的リスク対策を全て反映した改善版
 *
 * 主な変更点:
 * - サービス説明セクションの追加（公式との関係性明記）
 * - プロバイダ責任制限法対応の条項追加
 * - ログ保存・開示に関する明記
 * - 著作権・肖像権等の禁止事項を詳細化
 * - 権利者向けの削除依頼手順を明記
 */

import { useNavigate } from "react-router-dom";
import { ArrowLeft, ShieldAlert, AlertTriangle } from "lucide-react";
import { AtmosphereBackground } from "@/components/atoms/AtmosphereBackground";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export const AboutPage = () => {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen w-full text-white/90">
      <AtmosphereBackground />

      <div className="relative z-10 mx-auto max-w-3xl px-4 py-12">
        {/* Navigation Back */}
        <div className="mb-8">
          <Button
            variant="ghost"
            className="-ml-4 text-white/60 hover:bg-white/10 hover:text-white"
            onClick={() => {
              void navigate("/");
            }}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            トップに戻る
          </Button>
        </div>

        <header className="mb-12">
          <h1 className="mb-4 text-4xl font-bold tracking-tight text-white drop-shadow-sm">
            About Kvell
          </h1>
        </header>

        <div className="space-y-8">
          {/* 🆕 Section: Service Description */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-white/80">
              サービスについて
            </h2>
            <Card className="rounded-card border-white/10 bg-black/20 backdrop-blur-md">
              <CardContent className="space-y-4 p-6 text-sm leading-relaxed text-white/70">
                <p>
                  Kvellは、ユーザー同士が自由に会話を楽しむための匿名掲示板プラットフォームです。
                </p>

                <div className="rounded border-l-4 border-amber-500/50 bg-amber-900/20 p-4">
                  <div className="mb-2 flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-amber-400" />
                    <p className="font-bold text-white/90">重要なお知らせ</p>
                  </div>
                  <ul className="space-y-2 text-xs">
                    <li>
                      <strong>
                        本サービスは、特定の芸能人・アーティスト・団体・企業等の公式サービスではありません。
                      </strong>
                    </li>
                    <li>
                      本サービスは、いかなる公式団体とも提携・協力・承認・後援の関係にはありません。
                    </li>
                    <li>
                      投稿内容は全てユーザー個人の意見であり、運営者の見解を示すものではありません。
                    </li>
                    <li>
                      本サービスで言及される芸能人、アーティスト、番組名、企業名等の名称・商標は、それぞれの権利者に帰属します。
                    </li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Section: Terms of Service */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-white/80">利用規約</h2>
            <Card className="rounded-card border-white/10 bg-black/20 backdrop-blur-md">
              <CardContent className="space-y-4 p-6 text-sm leading-relaxed text-white/70">
                <h3 className="mb-2 font-bold text-white/90">利用規約</h3>
                <p>
                  本利用規約（以下「本規約」といいます。）は、本サービス（以下「当サービス」といいます。）の利用条件を定めるものです。ユーザーは、当サービスを利用することにより、本規約に同意したものとみなされます。
                </p>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  第1条（適用）
                </h4>
                <p>
                  本規約は、ユーザーと当サービス提供者との間の、当サービスの利用に関わる一切の関係に適用されます。
                </p>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  第2条（利用資格）
                </h4>
                <p>
                  当サービスは、18歳以上の方を対象としています。18歳未満の方は、保護者の同意を得た上でご利用ください。
                </p>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  第3条（禁止事項）
                </h4>
                <p>
                  ユーザーは、当サービスの利用にあたり、以下の行為をしてはなりません。
                </p>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  <li>法令または公序良俗に違反する行為</li>
                  <li>他者を誹謗中傷し、または不当に差別・攻撃する行為</li>
                  <li>
                    著作権、商標権、肖像権、パブリシティ権その他の知的財産権を侵害する行為
                  </li>
                  <li>歌詞、台本、記事、書籍等の全文または大部分の転載</li>
                  <li>公式以外のソースからの画像・動画の無断投稿・埋め込み</li>
                  <li>
                    会員限定コンテンツ、有料配信内容の詳細な書き起こし・ネタバレ
                  </li>
                  <li>本人が公開していない私的な写真・映像への言及</li>
                  <li>容姿・私生活に関する過度に侵襲的な投稿</li>
                  <li>
                    ストーカー行為に該当しうる執拗な追跡・監視に基づく投稿
                  </li>
                  <li>犯罪予告、脅迫、自殺教唆等の違法行為</li>
                  <li>当サービスの運営を妨害する行為</li>
                  <li>不正アクセス、またはこれを試みる行為</li>
                  <li>その他、運営者が不適切と判断する行為</li>
                </ul>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  第4条（投稿内容について）
                </h4>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  <li>
                    ユーザーが当サービスに投稿した内容の責任は、当該ユーザーに帰属します。
                  </li>
                  <li>
                    投稿内容は、ユーザー個人の感想・意見であり、運営者の見解を示すものではありません。
                  </li>
                  <li>
                    運営者は、投稿内容について事前の審査義務を負いません。
                  </li>
                  <li>
                    運営者は、法令違反や本規約違反のおそれがある投稿について、事前の通知なく削除・非表示等の対応を行うことがあります。
                  </li>
                  <li>
                    権利者からの正当な削除依頼があった場合、速やかに対応いたします。
                  </li>
                </ul>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  第5条（コンテンツの自動選別について）
                </h4>
                <p>
                  本サービスでは、ユーザーの反応に基づき、投稿を自動的に表示・非表示するアルゴリズムを使用しています。この選別は機械的な処理によるものであり、運営者が個別の投稿内容を事前審査・推奨するものではありません。
                </p>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  第6条（ログの保存と開示）
                </h4>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  <li>
                    運営者は、法令に基づく照会があった場合、または裁判所の命令がある場合、IPアドレス、アクセス日時等のログ情報を捜査機関・裁判所に開示します。
                  </li>
                  <li>
                    投稿時のIPアドレスおよびタイムスタンプは、法令で定める期間保存されます。
                  </li>
                  <li>
                    ユーザーは、本サービスが完全な匿名性を保証するものではないことに同意するものとします。
                  </li>
                </ul>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  第7条（違法情報等への対応）
                </h4>
                <ol className="mt-2 list-decimal space-y-2 pl-5">
                  <li>
                    運営者は、投稿内容が他者の権利を侵害していると信じるに足りる相当の理由があるときは、当該投稿の削除その他の送信防止措置を講じることがあります。
                  </li>
                  <li>
                    権利侵害を申告される方は、以下の情報を提供してください：
                    <ul className="mt-1 list-disc space-y-1 pl-5 text-xs">
                      <li>申告者の氏名・連絡先</li>
                      <li>侵害されたとする権利の内容</li>
                      <li>権利侵害に該当すると主張する投稿の特定情報</li>
                      <li>権利侵害であると判断する理由</li>
                    </ul>
                  </li>
                  <li>
                    当該内容を確認のうえ、法令および本規約に基づき、適切な対応を行います。
                  </li>
                </ol>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  第8条（サービスの提供・変更・停止）
                </h4>
                <p>
                  運営者は、ユーザーへの事前通知なく、当サービスの内容を変更、追加、または停止することがあります。
                </p>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  第9条（免責事項）
                </h4>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  <li>
                    当サービスは、現状有姿で提供されるものであり、完全性・正確性・有用性を保証するものではありません。
                  </li>
                  <li>
                    当サービスは、特定の芸能人・アーティスト・団体・企業等の公式サービスではなく、これらとの提携関係もありません。
                  </li>
                  <li>
                    投稿内容は全てユーザー個人によるものであり、運営者はその内容について一切の責任を負いません。
                  </li>
                  <li>
                    当サービスの利用により生じた損害について、運営者は一切の責任を負いません。
                  </li>
                </ul>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  第10条（準拠法・管轄裁判所）
                </h4>
                <ol className="mt-2 list-decimal space-y-1 pl-5">
                  <li>本規約の解釈にあたっては、日本法を準拠法とします。</li>
                  <li>
                    本サービスに関する紛争については、東京地方裁判所を第一審の専属的合意管轄裁判所とします。
                  </li>
                </ol>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  第11条（規約の変更）
                </h4>
                <p>
                  運営者は、必要と判断した場合、本規約を変更することができます。変更後の規約は、当サービス上に掲載された時点から効力を生じるものとします。
                </p>
              </CardContent>
            </Card>
          </section>

          {/* Section: Privacy Policy */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-white/80">
              プライバシーポリシー
            </h2>
            <Card className="rounded-card border-white/10 bg-black/20 backdrop-blur-md">
              <CardContent className="space-y-4 p-6 text-sm leading-relaxed text-white/70">
                <h3 className="mb-2 font-bold text-white/90">
                  プライバシーポリシー
                </h3>
                <p>
                  当サービスは、ユーザーのプライバシーを尊重し、以下の方針に基づき個人情報を取り扱います。
                </p>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  1. 取得する情報
                </h4>
                <p>当サービスでは、以下の情報を取得する場合があります。</p>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  <li>
                    通報・お問い合わせ時にユーザーが入力した情報（メールアドレス、内容等）
                  </li>
                  <li>
                    サーバーに自動的に記録されるアクセスログ（IPアドレス、ブラウザ種別、アクセス日時等）
                  </li>
                  <li>
                    投稿時のIPアドレス、タイムスタンプ、ブラウザフィンガープリント
                  </li>
                </ul>
                <p className="mt-2 text-xs text-white/40">
                  ※当サービスでは、ユーザー登録機能は提供していませんが、法令に基づく情報保存義務を履行するため、上記情報を記録します。
                </p>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  2. 利用目的
                </h4>
                <p>取得した情報は、以下の目的に限って利用します。</p>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  <li>サービスの提供・運営・改善のため</li>
                  <li>規約違反や不正利用への対応のため</li>
                  <li>通報・お問い合わせへの対応のため</li>
                  <li>法令に基づく捜査機関・裁判所への情報開示のため</li>
                </ul>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  3. 第三者提供について
                </h4>
                <p>
                  取得した個人情報は、法令に基づく場合（捜査機関からの照会、裁判所の命令等）を除き、ユーザーの同意なく第三者に提供することはありません。
                </p>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  4. 情報の保存期間
                </h4>
                <p>
                  IPアドレス、アクセスログ等の情報は、特定電気通信役務提供者の損害賠償責任の制限及び発信者情報の開示に関する法律（プロバイダ責任制限法）に基づき、一定期間保存されます。
                </p>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  5. 安全管理
                </h4>
                <p>
                  運営者は、取得した情報の漏えい・滅失・改ざん等を防止するため、合理的な安全対策を講じます。
                </p>

                <h4 className="mt-4 mb-2 font-bold text-white/80">
                  6. プライバシーポリシーの変更
                </h4>
                <p>
                  本ポリシーの内容は、必要に応じて変更されることがあります。変更後の内容は、当サービス上に掲載された時点で効力を生じます。
                </p>
              </CardContent>
            </Card>
          </section>

          {/* Section: Reporting */}
          <section>
            <h2 className="mb-4 flex items-center gap-2 text-2xl font-bold text-white/80">
              <ShieldAlert className="h-6 w-6 text-red-400" />
              通報・削除依頼
            </h2>
            <Card className="rounded-card border-red-500/20 bg-red-900/10 shadow-lg backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg text-white/90">
                  権利侵害・違反投稿の報告について
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 p-6 pt-0 text-white/70">
                <p>
                  本サービス上の投稿について、名誉毀損、著作権侵害、プライバシー侵害等の権利侵害、または利用規約に反する可能性があるとお考えの場合は、下記フォームよりご連絡ください。
                </p>

                <p>
                  ご連絡の際は、氏名及び連絡可能なメールアドレスのご入力をお願いいたします。
                  内容を確認のうえ、法令および本利用規約に基づき、必要に応じて
                  投稿の削除その他の適切な対応を行います。
                </p>

                <div className="mt-6">
                  <a
                    href="https://docs.google.com/forms/d/e/1FAIpQLSfZ-4LPUzr6IPtxk_zqCQoDdLG9jC-eRxNdkA236-cE-D-lXg/viewform?usp=dialog"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Button className="rounded-button shadow-glow-sm w-full overflow-hidden bg-red-600 px-6 py-2 font-bold text-white transition-all duration-300 hover:bg-red-500 sm:w-auto">
                      通報・削除依頼フォームへ
                    </Button>
                  </a>
                </div>
                <p className="mt-2 text-xs text-white/40">
                  ※ フォームは外部サイト（Google Forms）に移動します。
                </p>
              </CardContent>
            </Card>
          </section>

          <footer className="pt-12 pb-8 text-center text-sm text-white/20">
            &copy; 2025 Kvell. All rights reserved.
          </footer>
        </div>
      </div>
    </div>
  );
};
