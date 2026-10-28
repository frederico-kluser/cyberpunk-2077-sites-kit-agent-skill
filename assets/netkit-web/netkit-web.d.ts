declare module "netkit-web" {
  import type { CSSProperties, ReactElement, ReactNode } from "react"

  export const VERSION: string
  export const THEME_NAMES: readonly ["net", "corpo", "street", "tabloid", "neon"]
  export type ThemeName = (typeof THEME_NAMES)[number]
  export type Align = "start" | "center" | "end" | "stretch"
  export type TextAlign = "left" | "center" | "right"
  export type FontKey = "raj" | "orbitron" | "blender" | "industry" | "arial"
  export type Weight = "light" | "regular" | "medium" | "semibold" | "bold" | "black"
  export type Box4 = number | [number, number, number, number]
  /** Cor: sempre uma variável do sistema, ex. "var(--nk-accent)" ou "#5ef6ff" da paleta. */
  export type Color = string

  export interface Common {
    width?: number
    height?: number
    grow?: number
    selfAlign?: Align
    margin?: Box4
    opacity?: number
    /** id de página do site ou endereço completo (https://… ou NETdir://…) */
    link?: string
    hover?: Color
    name?: string
  }

  export interface BoxProps extends Common {
    children?: ReactNode
    padding?: Box4
    gap?: number
    align?: Align
    valign?: Align
    background?: Color
    border?: { color: Color; width: number }
    /** só em Row: empilha no telemóvel */
    stack?: boolean
  }

  export interface TextProps extends Common {
    children?: ReactNode
    as?: "p" | "h1" | "h2" | "h3" | "span"
    size?: number
    color?: Color
    font?: FontKey
    weight?: Weight
    upper?: boolean
    align?: TextAlign
    wrap?: number
    lineHeight?: number
    /** voz de título do tema (família, peso, cor e caixa) */
    heading?: boolean
  }

  export interface ImageProps extends Common {
    image: string
    tint?: Color
    fit?: "cover" | "contain"
    alt?: string
  }

  export interface SiteImage {
    url?: string
    file?: string
    atlas?: string
    part?: string
    description?: string
  }

  export interface PageProps extends Omit<BoxProps, "border" | "valign"> {
    id: string
    path?: string
    title?: string
  }

  export interface SiteProps {
    id: string
    title: string
    domain: string
    home?: string
    lang?: string
    icon?: string
    images?: Record<string, SiteImage>
    theme?: ThemeName
    children?: ReactNode
  }

  export interface NavItem {
    label: string
    /** id de página do site ou endereço */
    to: string
  }

  export interface SiteMeta {
    id: string
    title: string
    domain: string
    lang?: string
    home: string
    icon?: string
    images: Record<string, SiteImage>
    pages: { id: string; title: string; path: string; address: string }[]
  }

  export function Site(props: SiteProps): ReactElement
  export function Page(props: PageProps): ReactElement
  export function Column(props: BoxProps): ReactElement
  export function Row(props: BoxProps): ReactElement
  export function Stack(props: BoxProps): ReactElement
  export function Text(props: TextProps): ReactElement
  export function Image(props: ImageProps): ReactElement
  export function Rect(props: Common & { color?: Color }): ReactElement
  export function Spacer(props: Common): ReactElement

  export function NavBar(props: {
    items: NavItem[]
    active?: string
    gap?: number
    size?: number
    color?: Color
    activeColor?: Color
  }): ReactElement

  export function Header(props: {
    logo?: string
    logoSize?: number
    title: string
    subtitle?: string
    nav?: NavItem[]
    active?: string
  }): ReactElement

  export function Hero(props: {
    image?: string
    title: string
    text?: string
    cta?: NavItem
    height?: number
    align?: Align
  }): ReactElement

  export function Button(props: {
    label: string
    to: string
    variant?: "solid" | "outline"
    size?: number
    color?: Color
    textColor?: Color
  }): ReactElement

  export function Card(props: {
    image?: string
    title: string
    text?: string
    to?: string
    width?: number
    imageHeight?: number
    meta?: string
  }): ReactElement

  export function Grid(props: { columns?: number; gap?: number; children?: ReactNode }): ReactElement

  export function Section(props: { title: string; children?: ReactNode; gap?: number }): ReactElement

  export function Article(props: {
    title: string
    byline?: string
    body?: string[]
    width?: number
    image?: string
  }): ReactElement

  export function ProductCard(props: {
    image?: string
    name: string
    price: number | string
    to?: string
    width?: number
  }): ReactElement

  export function Divider(props: { color?: Color; thickness?: number; margin?: Box4 }): ReactElement
  export function Badge(props: { text: string; color?: Color; textColor?: Color }): ReactElement
  export function Quote(props: { text: string; author?: string; width?: number }): ReactElement
  export function BulletList(props: { items?: string[]; width?: number }): ReactElement

  export function Table(props: {
    columns?: string[]
    rows?: (string | number)[][]
    widths?: number[]
  }): ReactElement

  export function Banner(props: {
    image?: string
    text: string
    to?: string
    height?: number
    color?: Color
  }): ReactElement

  export function Footer(props: { text: string; links?: NavItem[] }): ReactElement

  export function useNav(): { meta: SiteMeta; images: Record<string, SiteImage>; href: (to?: string) => string | undefined; page: string }
  export function pagesOf(children: ReactNode): ReactElement<PageProps>[]
  export function siteMeta(props: SiteProps): SiteMeta
  export function textOf(children: ReactNode): string
  export function u(n: number): string
  export function pageHref(id: string): string

  /** Estilos inline só são legais dentro do kit; um site nunca os usa. */
  export type KitStyle = CSSProperties & Record<`--${string}`, string | number>
}
