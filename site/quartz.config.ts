import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

/**
 * Quartz 4 Configuration
 *
 * See https://quartz.jzhao.xyz/configuration for more information.
 */
const config: QuartzConfig = {
  configuration: {
    pageTitle: "Chance Encounters — Party Records",
    pageTitleSuffix: "",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "en-US",
    baseUrl: "notoriousWRG.github.io/memir",
    ignorePatterns: [
      "private",
      "templates",
      ".obsidian",
      ".claude",
      "site",
      "session_audio",
      "ledger",
      "planning.md",
      "_dashboard.md",
      "audit-log.md",
      "PLAYER-SITE-PLAN.md",
    ],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      typography: {
        header: "Cinzel",
        body: "Source Sans Pro",
        code: "IBM Plex Mono",
      },
      colors: {
        lightMode: {
          // Parchment companion — warm ivory + ink + bronze
          light: "#f5f0e8",
          lightgray: "#e0d8c8",
          gray: "#9a8e7e",
          darkgray: "#3d3328",
          dark: "#1e1a14",
          secondary: "#3a7a6e",
          tertiary: "#a06830",
          highlight: "rgba(160, 104, 48, 0.10)",
          textHighlight: "#c08a4e55",
        },
        darkMode: {
          // Storm & Bronze (primary)
          light: "#1c2530",
          lightgray: "#2c3744",
          gray: "#5a6b78",
          darkgray: "#cdd6dd",
          dark: "#e6ebef",
          secondary: "#6fb3a8",
          tertiary: "#c08a4e",
          highlight: "rgba(111, 179, 168, 0.12)",
          textHighlight: "#c08a4e55",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "git", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false, comments: true }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "katex" }),
    ],
    filters: [Plugin.ExplicitPublish()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
      // Comment out CustomOgImages to speed up build time
      Plugin.CustomOgImages(),
    ],
  },
}

export default config
