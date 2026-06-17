/**
 * Heroicons 图标映射 —— 将 Ant Design 图标统一替换为 Heroicons (24/outline)
 * 保持原有颜色不变，仅替换图标样式
 */
import React from "react";

// Heroicons v2 outline imports
import {
  CheckIcon,
  XMarkIcon,
  ClipboardDocumentIcon,
  TrashIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  DocumentTextIcon,
  HomeIcon,
  LinkIcon,
  PlusIcon,
  ArrowPathIcon,
  MagnifyingGlassIcon,
  PaperAirplaneIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  ClockIcon,
  CodeBracketIcon,
  BookOpenIcon,
  BugAntIcon,
  LightBulbIcon,
  CalendarDaysIcon,
  CameraIcon,
  PlayIcon,
  DocumentDuplicateIcon,
  MusicalNoteIcon,
  MapIcon,
  ChartBarIcon,
  ChartPieIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  FireIcon,
  FlagIcon,
  FolderIcon,
  FolderOpenIcon,
  FolderPlusIcon,
  GiftIcon,
  GlobeAltIcon,
  HeartIcon,
  EyeIcon,
  LockClosedIcon,
  EnvelopeIcon,
  ArrowRightStartOnRectangleIcon,
  Bars3Icon,
  Bars3BottomLeftIcon,
  Bars3BottomRightIcon,
  ChatBubbleLeftIcon,
  SignalIcon,
  PhotoIcon,
  SignalSlashIcon,
  StarIcon,
  PlayCircleIcon,
  PauseCircleIcon,
  StopIcon,
  ArrowUturnLeftIcon,
  ArrowUturnRightIcon,
  ShieldCheckIcon,
  ShieldExclamationIcon,
  CloudArrowUpIcon,
  BookmarkIcon,
  ShareIcon,
  Squares2X2Icon,
  CubeIcon,
  CpuChipIcon,
  WrenchIcon,
  UserIcon,
  UserGroupIcon,
  TrophyIcon,
  RocketLaunchIcon,
  BoltIcon,
  CursorArrowRaysIcon,
  ServerIcon,
  CommandLineIcon,
  CubeTransparentIcon,
  BeakerIcon,
  AcademicCapIcon,
  MegaphoneIcon,
  BuildingOffice2Icon,
  RectangleStackIcon,
  Cog6ToothIcon,
  DocumentCheckIcon,
  DocumentMagnifyingGlassIcon,
  CommandLineIcon as TerminalIcon,
} from "@heroicons/react/24/outline";

type IconProps = {
  className?: string;
  style?: React.CSSProperties;
};

// Ant Design → Heroicons 映射表
const iconMap: Record<string, React.FC<IconProps>> = {
  // 导航 & 操作
  HomeOutlined: HomeIcon,
  SearchOutlined: MagnifyingGlassIcon,
  PlusOutlined: PlusIcon,
  DeleteOutlined: TrashIcon,
  EditOutlined: PencilIcon,
  CopyOutlined: ClipboardDocumentIcon,
  SaveOutlined: BookmarkIcon,
  SendOutlined: PaperAirplaneIcon,
  ReloadOutlined: ArrowPathIcon,
  RedoOutlined: ArrowPathIcon,
  UndoOutlined: ArrowUturnLeftIcon,
  RotateRightOutlined: ArrowUturnRightIcon,
  UploadOutlined: CloudArrowUpIcon,
  DownloadOutlined: ArrowDownIcon,
  LinkOutlined: LinkIcon,
  ShareAltOutlined: ShareIcon,
  ExpandOutlined: Square2StackIcon,
  SplitCellsOutlined: Square2StackIcon,
  ClearOutlined: XMarkIcon,
  CloseOutlined: XMarkIcon,
  MenuOutlined: Bars3Icon,
  MenuFoldOutlined: Bars3BottomLeftIcon,
  MenuUnfoldOutlined: Bars3BottomRightIcon,
  SettingOutlined: Cog6ToothIcon,
  LogoutOutlined: ArrowRightStartOnRectangleIcon,

  // 状态 & 反馈
  CheckOutlined: CheckIcon,
  CheckCircleOutlined: CheckCircleIcon,
  CloseCircleOutlined: XCircleIcon,
  ExclamationCircleOutlined: ExclamationCircleIcon,
  InfoCircleOutlined: InformationCircleIcon,
  WarningOutlined: ExclamationCircleIcon,
  QuestionCircleOutlined: InformationCircleIcon,
  SafetyOutlined: ShieldCheckIcon,
  SafetyCertificateOutlined: ShieldCheckIcon,
  LoadingOutlined: ArrowPathIcon,

  // 文件 & 文档
  FileTextOutlined: DocumentTextIcon,
  FileExcelOutlined: DocumentTextIcon,
  FilePdfOutlined: DocumentTextIcon,
  FolderOutlined: FolderIcon,
  FolderOpenOutlined: FolderOpenIcon,
  FolderPlusOutlined: FolderPlusIcon,

  // 媒体 & 内容
  PictureOutlined: PhotoIcon,
  CameraOutlined: CameraIcon,
  PlayCircleOutlined: PlayCircleIcon,
  PauseCircleOutlined: PauseCircleIcon,
  VideoCameraOutlined: CameraIcon,
  CodeOutlined: CodeBracketIcon,
  ReadOutlined: BookOpenIcon,
  BookOutlined: BookOpenIcon,

  // 通讯 & 社交
  MessageOutlined: ChatBubbleLeftIcon,
  MailOutlined: EnvelopeIcon,
  BellOutlined: BellIcon,
  LikeOutlined: HeartIcon,
  DislikeOutlined: HeartIcon,
  StarOutlined: StarIcon,
  HeartOutlined: HeartIcon,

  // 用户 & 团队
  UserOutlined: UserIcon,
  TeamOutlined: UserGroupIcon,

  // 数据 & 图表
  BarChartOutlined: ChartBarIcon,
  PieChartOutlined: ChartPieIcon,
  LineChartOutlined: ChartBarIcon,
  DashboardOutlined: Squares2X2Icon,
  RiseOutlined: ArrowTrendingUpIcon,
  FallOutlined: ArrowTrendingDownIcon,
  DatabaseOutlined: ServerIcon,

  // 导向 & 方向
  ArrowLeftOutlined: ArrowLeftIcon,
  ArrowRightOutlined: ArrowRightIcon,
  UpOutlined: ArrowUpIcon,
  DownOutlined: ArrowDownIcon,
  AimOutlined: CursorArrowRaysIcon,

  // 工具 & 系统
  RobotOutlined: CpuChipIcon,
  ThunderboltOutlined: BoltIcon,
  RocketOutlined: RocketLaunchIcon,
  FireOutlined: FireIcon,
  FlagOutlined: FlagIcon,
  TrophyOutlined: TrophyIcon,
  GiftOutlined: GiftIcon,
  ExperimentOutlined: BeakerIcon,
  MedicineBoxOutlined: BeakerIcon,
  NodeIndexOutlined: MapIcon,
  ApartmentOutlined: MapIcon,
  ProjectOutlined: RectangleStackIcon,
  CubeOutlined: CubeIcon,
  GlobalOutlined: GlobeAltIcon,
  LockOutlined: LockClosedIcon,
  EyeOutlined: EyeIcon,
  EnvironmentOutlined: BuildingOffice2Icon,

  // 文本 & 格式
  BulbOutlined: LightBulbIcon,
  InfoOutlined: InformationCircleIcon,
  TagOutlined: BookmarkIcon,

  // 时间
  ClockCircleOutlined: ClockIcon,
  HistoryOutlined: ClockIcon,
  CalendarOutlined: CalendarDaysIcon,

  // 其他
  BugOutlined: BugAntIcon,
  CompassOutlined: CompassIcon,
  StepForwardOutlined: PlayIcon,
  CrownOutlined: CheckBadgeIcon,
  SwapOutlined: ArrowPathIcon,
  CaretRightOutlined: PlayIcon,
  PauseOutlined: StopIcon,
  AlertOutlined: ExclamationCircleIcon,
  LockFilled: LockClosedIcon,
  FlagFilled: FlagIcon,
  CheckCircleFilled: CheckCircleIcon,
};

// 补充几个特殊图标
function PencilIcon(props: IconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
      {...props}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10"
      />
    </svg>
  );
}

function CompassIcon(props: IconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
      {...props}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z"
      />
    </svg>
  );
}

function Square2StackIcon(props: IconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
      {...props}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75"
      />
    </svg>
  );
}

function BellIcon(props: IconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
      {...props}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0"
      />
    </svg>
  );
}

function CheckBadgeIcon(props: IconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
      {...props}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
      />
    </svg>
  );
}

/**
 * HeroIcon 组件 —— 统一的图标渲染组件
 * @param name - Ant Design 图标名称（如 "CheckOutlined"）
 * @param className - CSS 类名
 * @param style - 内联样式
 */
export const HeroIcon: React.FC<{
  name: string;
  className?: string;
  style?: React.CSSProperties;
}> = ({ name, className = "w-5 h-5", style }) => {
  const IconComponent = iconMap[name];

  if (!IconComponent) {
    // 未知图标回退为问号
    return (
      <span className={className} style={style}>
        ?
      </span>
    );
  }

  return <IconComponent className={className} style={style} />;
};

export default HeroIcon;
