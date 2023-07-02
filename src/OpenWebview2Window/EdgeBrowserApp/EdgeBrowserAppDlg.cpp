//Author: Ayush Chaudhary
//Email: ayush.shyam@gmail.com
//License: Free license 
//Description: In this application I show how to use webview2 edge browser in yoor dialog based applications.
// Very easy implementation of webview

#include "stdafx.h"
#include "afxdialogex.h"
//#include "framework.h"
#include "EdgeBrowserApp.h"
#include "EdgeBrowserAppDlg.h"
#include "winuser.h"
#include "ViewComponent.h"
//#include "pch.h"
#include <ShObjIdl_core.h>
#include <Shellapi.h>
#include <ShlObj_core.h>
//#include <wrl.h>
//#include <winrt/windows.system.h>

#ifdef __windows__
#undef __windows__
#endif

#include "ParseOptions.cpp"
static woptmap_t opts;
void get_options(void) {
    opts = warg2optmap(splitwargs(AfxGetApp()->m_lpCmdLine));
}


#define READ_STRUCT(var_name) \
    HANDLE var_name##_fin = CreateFile(L# var_name, GENERIC_READ, 0, NULL, OPEN_EXISTING, 0, 0); \
    ReadFile(var_name##_fin, &var_name, sizeof(var_name), NULL, NULL); \
    CloseHandle(var_name##_fin);

#define WRITE_STRUCT(var_name) \
    HANDLE var_name##_fout = CreateFile(L# var_name, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, 0, 0); \
    WriteFile(var_name##_fout, &var_name, sizeof(var_name), NULL, NULL); \
    CloseHandle(var_name##_fout);

typedef struct window_pos_t_tag {
    long x;
    long y;
    long width;
    long height;
} window_pos_t;

#define CRECT2WPOS(crect, wpos) \
    wpos.x = crect.left; wpos.width  = crect.Width(); \
    wpos.y = crect.top ; wpos.height = crect.Height();

window_pos_t get_default_pos(void) {
    HDC shdc = GetDC(0);
    int screen_x = GetDeviceCaps(shdc, 118);
    int screen_y = GetDeviceCaps(shdc, 117);
    window_pos_t ret;
    ret.x = screen_x / 4;
    ret.y = screen_y / 4;
    ret.width  = screen_x / 2;
    ret.height = screen_y / 2;
    return ret;
}

static constexpr UINT s_runAsyncWindowMessage = WM_APP;

// CEdgeBrowserAppDlg dialog

CEdgeBrowserAppDlg::CEdgeBrowserAppDlg(CWnd* pParent /*=nullptr*/)
    : CDialog(IDD_EDGEBROWSERAPP_DIALOG, pParent)
{
    m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
    g_hInstance = GetModuleHandle(NULL);

}

void CEdgeBrowserAppDlg::DoDataExchange(CDataExchange* pDX)
{
    CDialog::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CEdgeBrowserAppDlg, CDialog)
    ON_WM_SYSCOMMAND()
    ON_WM_PAINT()
    ON_WM_QUERYDRAGICON()
    ON_WM_SIZE()
    ON_WM_CLOSE()
END_MESSAGE_MAP()

void CEdgeBrowserAppDlg::OnSize(UINT a, int b, int c)
{
    ResizeEverything();
}

void CEdgeBrowserAppDlg::OnClose() 
{
    // save window pos
    CRect window_crect; window_pos_t window_pos;
    this->GetWindowRect(&window_crect);
    CRECT2WPOS(window_crect, window_pos);
    WRITE_STRUCT(window_pos);
    
    CDialog::OnClose();
}

// CEdgeBrowserAppDlg message handlers

BOOL CEdgeBrowserAppDlg::OnInitDialog()
{
    CDialog::OnInitDialog();

    HRESULT hresult = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED | COINIT_DISABLE_OLE1DDE);

    SetWindowLongPtr(this->GetSafeHwnd(), GWLP_USERDATA, (LONG_PTR)this);

    //CMenu* pSysMenu = GetSystemMenu(FALSE);
    //if (pSysMenu != nullptr)
    //{
    //    BOOL bNameValid;
    //    CString strAboutMenu;
    //    bNameValid = strAboutMenu.LoadString(IDS_ABOUTBOX);
    //    ASSERT(bNameValid);
    //    if (!strAboutMenu.IsEmpty())
    //    {
    //        pSysMenu->AppendMenu(MF_SEPARATOR);
    //        pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
    //    }
    //}

    // Set the icon for this dialog.  The framework does this automatically
    //  when the application's main window is not a dialog
    SetIcon(m_hIcon, TRUE);			// Set big icon
    SetIcon(m_hIcon, FALSE);		// Set small icon

    // enable maximize and minimize button (so sorry I don't have a VS installation)
    SetWindowLong(this->m_hWnd, GWL_STYLE, GetWindowLong(this->m_hWnd, GWL_STYLE) | WS_MINIMIZEBOX);
    SetWindowLong(this->m_hWnd, GWL_STYLE, GetWindowLong(this->m_hWnd, GWL_STYLE) | WS_MAXIMIZEBOX);

    // save options to global static opts
    get_options();

    // set window title
    std::wstring window_title_key_str = L"--window-title";
    const wchar_t *window_title = opts[window_title_key_str].c_str();
    this->SetWindowText(window_title);

    // resize window
	window_pos_t window_pos;
    if (PathFileExists(L"window_pos")) { READ_STRUCT(window_pos); }
                                  else { window_pos = get_default_pos(); }
	this->MoveWindow(window_pos.x, window_pos.y, window_pos.width, window_pos.height, TRUE);

    // TODO: Add extra initialization here
    InitializeWebView();

    return TRUE;  // return TRUE  unless you set the focus to a control
}


void CEdgeBrowserAppDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
    if ((nID & 0xFFF0) == IDM_ABOUTBOX)
    {

    }
    else
    {
        CDialog::OnSysCommand(nID, lParam);
    }
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CEdgeBrowserAppDlg::OnPaint()
{
    if (IsIconic())
    {
        CPaintDC dc(this); // device context for painting

        SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

        // Center icon in client rectangle
        int cxIcon = GetSystemMetrics(SM_CXICON);
        int cyIcon = GetSystemMetrics(SM_CYICON);
        CRect rect;
        GetClientRect(&rect);
        int x = (rect.Width() - cxIcon + 1) / 2;
        int y = (rect.Height() - cyIcon + 1) / 2;

        // Draw the icon
        dc.DrawIcon(x, y, m_hIcon);
    }
    else
    {
        CDialog::OnPaint();
    }
}

// The system calls this function to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR CEdgeBrowserAppDlg::OnQueryDragIcon()
{
    return static_cast<HCURSOR>(m_hIcon);
}
// Register the Win32 window class for the app window.

void CEdgeBrowserAppDlg::ResizeEverything()
{
    RECT availableBounds = { 0 };
    GetClientRect(&availableBounds);
    // ClientToScreen(&availableBounds);

    if (auto view = GetComponent<ViewComponent>())
    {
        view->SetBounds(availableBounds);
    }
}

void CEdgeBrowserAppDlg::RunAsync(std::function<void()> callback)
{
    auto* task = new std::function<void()>(callback);
    PostMessage(s_runAsyncWindowMessage, reinterpret_cast<WPARAM>(task), 0);
}

void CEdgeBrowserAppDlg::InitializeWebView()
{

    CloseWebView();
    m_dcompDevice = nullptr;


    HRESULT hr2 = DCompositionCreateDevice2(nullptr, IID_PPV_ARGS(&m_dcompDevice));
    if (!SUCCEEDED(hr2))
    {
        AfxMessageBox(L"Attempting to create WebView using DComp Visual is not supported.\r\n"
            "DComp device creation failed.\r\n"
            "Current OS may not support DComp.\r\n"
            "Create with Windowless DComp Visual Failed", MB_OK);
        return;
    }


#ifdef USE_WEBVIEW2_WIN10
    m_wincompCompositor = nullptr;
#endif
    LPCWSTR subFolder = nullptr;
    auto options = Microsoft::WRL::Make<CoreWebView2EnvironmentOptions>();
    options->put_AllowSingleSignOnUsingOSPrimaryAccount(FALSE);
    
    std::wstring userdata_path_key_str = L"--userdata-path";
    const wchar_t *userdata_path = opts[userdata_path_key_str].c_str();

    HRESULT hr = CreateCoreWebView2EnvironmentWithOptions(subFolder, userdata_path, options.Get(), Microsoft::WRL::Callback<ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler>(this, &CEdgeBrowserAppDlg::OnCreateEnvironmentCompleted).Get());
    //HRESULT hr = CreateCoreWebView2EnvironmentWithOptions(subFolder, nullptr, options.Get(), Microsoft::WRL::Callback<ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler>(this, &CEdgeBrowserAppDlg::OnCreateEnvironmentCompleted).Get());

    if (!SUCCEEDED(hr))
    {
        if (hr == HRESULT_FROM_WIN32(ERROR_FILE_NOT_FOUND))
        {
            TRACE("Couldn't find Edge installation. Do you have a version installed that is compatible with this ");
        }
        else
        {
            AfxMessageBox(L"Failed to create webview environment");
        }
    }
}

HRESULT CEdgeBrowserAppDlg::DCompositionCreateDevice2(IUnknown* renderingDevice, REFIID riid, void** ppv)
{
    HRESULT hr = E_FAIL;
    static decltype(::DCompositionCreateDevice2)* fnCreateDCompDevice2 = nullptr;
    if (fnCreateDCompDevice2 == nullptr)
    {
        HMODULE hmod = ::LoadLibraryEx(L"dcomp.dll", nullptr, 0);
        if (hmod != nullptr)
        {
            fnCreateDCompDevice2 = reinterpret_cast<decltype(::DCompositionCreateDevice2)*>(
                ::GetProcAddress(hmod, "DCompositionCreateDevice2"));
        }
    }
    if (fnCreateDCompDevice2 != nullptr)
    {
        hr = fnCreateDCompDevice2(renderingDevice, riid, ppv);
    }
    return hr;
}

void CEdgeBrowserAppDlg::CloseWebView(bool cleanupUserDataFolder)
{

    if (m_controller)
    {
        m_controller->Close();
        m_controller = nullptr;
        m_webView = nullptr;
    }
    m_webViewEnvironment = nullptr;
    if (cleanupUserDataFolder)
    {
        //Clean user data        
    }
}

HRESULT CEdgeBrowserAppDlg::OnCreateEnvironmentCompleted(HRESULT result, ICoreWebView2Environment* environment)
{
    m_webViewEnvironment = environment;
    m_webViewEnvironment->CreateCoreWebView2Controller(this->GetSafeHwnd(), Microsoft::WRL::Callback<ICoreWebView2CreateCoreWebView2ControllerCompletedHandler>(this, &CEdgeBrowserAppDlg::OnCreateCoreWebView2ControllerCompleted).Get());

    return S_OK;
}

HRESULT CEdgeBrowserAppDlg::OnCreateCoreWebView2ControllerCompleted(HRESULT result, ICoreWebView2Controller* controller)
{
    if (result == S_OK)
    {
        m_controller = controller;
        Microsoft::WRL::ComPtr<ICoreWebView2> coreWebView2;
        m_controller->get_CoreWebView2(&coreWebView2);
        //coreWebView2.query_to(&m_webView);
        m_webView = coreWebView2.Get();

        NewComponent<ViewComponent>(
            this, m_dcompDevice.Get(),
#ifdef USE_WEBVIEW2_WIN10
            m_wincompCompositor,
#endif
            m_creationModeId == IDM_CREATION_MODE_TARGET_DCOMP);

        if (!m_webView)
            return S_FALSE;

        std::wstring navigate_url_key_str = L"--navigate-url";
        const wchar_t *navigate_url = opts[navigate_url_key_str].c_str();
        HRESULT hresult = m_webView->Navigate(navigate_url);

        if (hresult == S_OK)
        {
            TRACE("Web Page Opened Successfully");
            ResizeEverything();
        }

    }
    else
    {
        TRACE("Failed to create webview");
    }
    return S_OK;
}

