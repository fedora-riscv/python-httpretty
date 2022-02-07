%global github_owner    gabrielfalcao
%global github_name     HTTPretty
%global srcname         httpretty
# define these only if actually building from a GH snapshot not a release tarball
#global github_commit   70af1f8cf925ef50cb5e72212fb0aa46e1451dc3
#global shortcommit     %%(c=%%{github_commit}; echo ${c:0:7})
#global github_date     20161011

%global run_tests 1

Name:           python-httpretty
Version:        1.1.4
# If github_date is defined, assume a post-release snapshot
Release:        6%{?github_date:.%{github_date}git%{shortcommit}}%{?dist}
Summary:        HTTP request mock tool for Python

License:        MIT
URL:            https://github.com/%{github_owner}/%{github_name}
Source0:        %{pypi_source}
# Alternative for building from a github snapshot
#Source0:        https://github.com/%%{github_owner}/%%{github_name}/archive/%%{github_commit}/%%{github_name}-%%{shortcommit}.tar.gz

# Avoid unnecessary remote access requirement (note: test only actually
# does a remote connection after PR #313)
Patch1: python-httpretty-fakesock_getpeercert_noconnect.patch

# Remote access (these tests were skipped upstream in <= 0.9.7)
Patch2: skip-test_passthrough.patch

# Remove timeout, which causes some tests to fail in Koji
#
# Fixes RHBZ#2046877
Patch3: test_response-no-within.patch

BuildArch:      noarch

%global _description\
Once upon a time a python developer wanted to use a RESTful API, everything was\
fine but until the day he needed to test the code that hits the RESTful API:\
what if the API server is down? What if its content has changed?\
Don't worry, HTTPretty is here for you.

%description %_description

%package -n python3-httpretty
Summary:        HTTP request mock tool for Python 3
Requires:       python%{python3_pkgversion}-six

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
# For tests
BuildRequires:  python%{python3_pkgversion}-httplib2
BuildRequires:  python%{python3_pkgversion}-mock
BuildRequires:  python%{python3_pkgversion}-nose
BuildRequires:  python%{python3_pkgversion}-requests
BuildRequires:  python%{python3_pkgversion}-sure
BuildRequires:  python%{python3_pkgversion}-urllib3
BuildRequires:  python%{python3_pkgversion}-tornado
BuildRequires:  python%{python3_pkgversion}-eventlet
BuildRequires:  python%{python3_pkgversion}-freezegun
BuildRequires:  python%{python3_pkgversion}-redis

%description -n python3-httpretty
Once upon a time a python developer wanted to use a RESTful API, everything was
fine but until the day he needed to test the code that hits the RESTful API:
what if the API server is down? What if its content has changed?
Don't worry, HTTPretty is here for you.


%prep
%autosetup -n httpretty-%{version} -p1

# Alternative for building from commit tarball
#autosetup -n %%{github_name}-%%{github_commit} -p1

# nose plugins we don't have yet
sed -i 's/^with-randomly = 1$//' setup.cfg
sed -i 's/^rednose = 1$//' setup.cfg

%build
%py3_build

%install
%py3_install

%check
%if %{run_tests}
%{__python3} -m nose -v
%endif

%files -n python3-httpretty
%doc README.rst
%license COPYING
%{python3_sitelib}/httpretty
%{python3_sitelib}/httpretty-%{version}-py%{python3_version}.egg-info


%changelog
%autochangelog
