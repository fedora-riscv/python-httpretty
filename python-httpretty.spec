%if 0%{?fedora}
# escaping for EPEL.
%global with_python3 0
%endif

%global run_tests 0

Name:           python-httpretty
Version:        0.8.3
Release:        2%{?dist}
Summary:        HTTP request mock tool for Python

License:        MIT
URL:            http://falcao.it/HTTPretty/
Source0:        https://pypi.python.org/packages/source/h/httpretty/httpretty-%{version}.tar.gz

# something about setuptools fails when it loads files with unicode characters
# in a non-unicode environment (like packaging build servers). Remove the
# unicode characters.
Patch0:         0001-Replace-unicode-character-with-ASCII.patch

# Part of https://github.com/gabrielfalcao/HTTPretty/pull/180
# however will likely still be needed for test-requirements in future.
Patch1:         0002-Un-pin-requirements.patch

BuildArch:      noarch

Requires:       python-urllib3

BuildRequires:  python2-devel
BuildRequires:  python-setuptools

%description
Once upon a time a python developer wanted to use a RESTful API, everything was
fine but until the day he needed to test the code that hits the RESTful API:
what if the API server is down? What if its content has changed?

Don't worry, HTTPretty is here for you.

%if 0%{?with_python3}
%package -n python3-httpretty
Summary:        HTTP request mock tool for Python 3
Requires:       python3-urllib3

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

%description -n python3-httpretty
Once upon a time a python developer wanted to use a RESTful API, everything was
fine but until the day he needed to test the code that hits the RESTful API:
what if the API server is down? What if its content has changed?

Don't worry, HTTPretty is here for you.
%endif

%prep
%setup -q -n httpretty-%{version}
%patch0 -p1
%patch1 -p1

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
%endif

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python2} setup.py build

%if 0%{?with_python3}
pushd %{py3dir}
CFLAGS="$RPM_OPT_FLAGS" %{__python3} setup.py build
popd
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
popd
%endif


%check
# There are a number of problems with the tests upstream.
# Interdependencies, only working on specific pinned versions, timing issues
# across tests. They are disabled for now but should be reenabled when possible.
%if %{run_tests}
%{__python2} setup.py test

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py test
popd
%endif
%endif


%files
%doc COPYING README.md
%{python_sitelib}/httpretty
%{python_sitelib}/httpretty-%{version}-py2.?.egg-info

%if 0%{?with_python3}
%files -n python3-httpretty
%doc COPYING README.md
%{python3_sitelib}/httpretty
%{python3_sitelib}/httpretty-%{version}-py3.?.egg-info
%endif


%changelog
* Tue Feb 24 2015 Jamie Lennox <jamielennox@redhat.com> - 0.8.3-2
- Added with_python3 build flags to enable building on EPEL.

* Mon Jul 28 2014 Jamie Lennox <jamielennox@redhat.com> - 0.8.3-1
- Updated to new version.
- Removed check, there are simply too many problems upstream.

* Mon Mar 10 2014 Jamie Lennox <jamielennox@redhat.com> - 0.8.0-1
- Initial package.

