%define		cmodule		/etc/sysconfig/sensors_modules
%define		cdaemon		/etc/sysconfig/sensors
%define		smodule		/etc/rc.d/init.d/sensors_modules
%define		sdaemon		/etc/rc.d/init.d/sensors

Summary:	lm_sensors configuration files
Summary(pl.UTF-8):   Pliki konfiguracyjne lm_sensors
Name:		lm_sensors-config
Version:	0.0.1
Release:	1
License:	GPL
Group:		Applications/System
Source0:	sensors_modules.sysconfig
# Sources from 100 are motherboard specific %{_sysconfdir}/sensors files
Source100:	sensors.conf.epox-EP-8K9A
Source101:	sensors.conf.ecs-K7VTA3
Source102:	sensors.conf.ecs-KT600-A
URL:		http://www.lm-sensors.org/wiki/Configurations
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Configuration files for lm_sensors.

%description -l pl.UTF-8
Pliki konfiguracyjne lm_sensors.

%package epox-EP-8K9A
Summary:	lm_sensors configuration files
Summary(pl.UTF-8):   Pliki konfiguracyjne lm_sensors
Group:		Applications/System
Requires:	lm_sensors
Provides:	%{name}

%description epox-EP-8K9A
lm_sensors configuration files for Epox 8K9A series motherboards
(tested with EP-8K9AI motherboard).

%description epox-EP-8K9A -l pl.UTF-8
Pliki konfiguracyjne lm_sensors dla płyt głównych z serii Epox 8K9A
(testowane na płycie EP-8K9AI).

%package ecs-K7VTA3
Summary:	lm_sensors configuration files
Summary(pl.UTF-8):   Pliki konfiguracyjne lm_sensors
Group:		Applications/System
Provides:	%{name}
Requires:	lm_sensors

%description ecs-K7VTA3
lm_sensors configuration files for ECS K7VTA3 series motherboards
(tested with K7VTA3 v. 5.0).

%description ecs-K7VTA3 -l pl.UTF-8
Pliki konfiguracyjne lm_sensors dla płyt głównych z serii ECS K7VTA3
(testowane na płycie K7VTA3 v. 5.0).

%package ecs-KT600-A
Summary:	lm_sensors configuration files
Summary(pl.UTF-8):   Pliki konfiguracyjne lm_sensors
Group:		Applications/System
Provides:	%{name}
Requires:	lm_sensors

%description ecs-KT600-A
lm_sensors configuration files for ECS KT600-A motherboard.

%description ecs-KT600-A -l pl.UTF-8
Pliki konfiguracyjne lm_sensors dla płyty głównej ECS KT600-A.

%prep
%setup -q -c -T
mkdir src
mkdir etc
mkdir sysconfig
cp %{SOURCE100} src
cp %{SOURCE101} src
cp %{SOURCE102} src

%build
rm -f etc/* sysconfig/*

mk_filelist() {
	cat > files.$1 << EOF
%defattr(644,root,root,755)
%%config(noreplace) %%verify(not md5 mtime size) %{_sysconfdir}/sensors.conf.$1
%%config(noreplace) %%verify(not md5 mtime size) /etc/sysconfig/sensors_modules.$1
%%ghost %{_sysconfdir}/sensors.conf
%%ghost /etc/sysconfig/sensors_modules
EOF
}

mk_post() {
	cat > post.$1 << EOF
ln -sf %{_sysconfdir}/sensors.conf.$1 %{_sysconfdir}/sensors.conf
ln -sf /etc/sysconfig/sensors_modules.$1 /etc/sysconfig/sensors_modules
if [ -f "%{smodule}" ]; then
	/sbin/chkconfig --add sensors_modules
	%%service sensors_modules restart "sensors modules"
fi
if [ -f "%{sdaemon}" ]; then
	/sbin/chkconfig --add sensors
	%%service sensors restart "sensors daemon"
fi
EOF
}

mk_preun() {
	cat > preun.$1 << EOF
if [ "$1" = "0" ]; then
	if [ -f "%{sdaemon}" ]; then
		%%service sensors stop
		/sbin/chkconfig --del sensors
	fi
	if [ -f "%{smodule}" ]; then
		%%service sensors_modules stop
		/sbin/chkconfig --del sensors_modules
	fi
fi
EOF
}

for FILE in src/sensors.conf.*
do
	MB=`echo $FILE | sed s:src/sensors.conf.::`
	mk_filelist $MB
	mk_post $MB
	mk_preun $MB
	BUS=`cat $FILE | grep "^BUS="`
	CHIP=`cat $FILE | grep "^CHIP="`
	cat $FILE | egrep -v "^BUS=|^CHIP=" > etc/sensors.conf.$MB
	cat %{SOURCE0} | \
		sed "s:^BUS=:$BUS:" | \
		sed "s:^CHIP=:$CHIP:" | \
		sed "s:#SENSORS_SET=1:SENSORS_SET=1:" \
		> sysconfig/sensors_modules.$MB
done

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/sysconfig
cp etc/* $RPM_BUILD_ROOT%{_sysconfdir}
cp sysconfig/* $RPM_BUILD_ROOT/etc/sysconfig

ln -sf /dev/null $RPM_BUILD_ROOT/etc/sysconfig/sensors_modules
ln -sf /dev/null $RPM_BUILD_ROOT%{_sysconfdir}/sensors.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post	epox-EP-8K9A -f post.epox-EP-8K9A
%preun	epox-EP-8K9A -f preun.epox-EP-8K9A
%files	epox-EP-8K9A -f files.epox-EP-8K9A

%post	ecs-K7VTA3 -f post.ecs-K7VTA3
%preun	ecs-K7VTA3 -f preun.ecs-K7VTA3
%files	ecs-K7VTA3 -f files.ecs-K7VTA3

%post	ecs-KT600-A -f post.ecs-KT600-A
%preun	ecs-KT600-A -f preun.ecs-KT600-A
%files	ecs-KT600-A -f files.ecs-KT600-A
