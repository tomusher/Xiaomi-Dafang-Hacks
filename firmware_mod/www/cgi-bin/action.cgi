#!/bin/sh

echo "Content-type: text/html"
echo "Pragma: no-cache"
echo "Cache-Control: max-age=0, no-store, no-cache"
echo ""

source ./func.cgi
source /system/sdcard/scripts/common_functions.sh

export LD_LIBRARY_PATH=/system/lib
export LD_LIBRARY_PATH=/thirdlib:$LD_LIBRARY_PATH

if [ -n "$F_cmd" ]; then
  if [ -z "$F_val" ]; then
    F_val=100
  fi
  case "$F_cmd" in
    showlog)
      echo "<pre>"
      case "${F_logname}" in
        "" | 1)
            echo "Summary of all log files:<br/>"
            tail /var/log/*
            ;;
        2)
            echo "Content of dmesg<br/>"
            /bin/dmesg
            ;;
        3)
            echo "Content of logcat<br/>"
            /system/bin/logcat -d
            ;;
        4)
          echo "Content of v4l2rtspserver-master.log<br/>"
          cat /system/sdcard/log/v4l2rtspserver-master.log
          ;;
        5)
          echo "Content of update.log <br/>"
          cat /system/sdcard/log/update.log
          ;;

      esac
      echo "</pre>"
      return
    ;;
    clearlog)
      echo "<pre>"
      case "${F_logname}" in
        "" | 1)
            echo "Summary of all log files cleared<br/>"
            for i in /var/log/*
            do
                echo -n "" > $i
            done
            ;;
        2)
            echo "Content of dmesg cleared<br/>"
            /bin/dmesg -c > /dev/null
            ;;
        3)
            echo "Content of logcat cleared<br/>"
            /system/bin/logcat -c
            ;;
        4)
          echo "Content of v4l2rtspserver-master.log cleared<br/>"
          echo -n "" > /system/sdcard/log/v4l2rtspserver-master.log
          ;;
        5)
          echo "Content of update.log cleared <br/>"
          echo -n "" > /system/sdcard/log/update.log
         ;;
      esac
      echo "</pre>"
      return
    ;;
    reboot)
      echo "Rebooting device..."
      /sbin/reboot
      return
    ;;

    shutdown)
      echo "Shutting down device.."
      /sbin/halt
      return
    ;;

    blue_led_on)
      setgpio 38 1
      setgpio 39 0
    ;;

    blue_led_off)
      setgpio 39 1
    ;;

    yellow_led_on)
      setgpio 38 0
      setgpio 39 1
    ;;

    yellow_led_off)
      setgpio 38 1
    ;;

    ir_led_on)
      setgpio 49 0
    ;;

    ir_led_off)
      setgpio 49 1
    ;;

    ir_cut_on)
      setgpio 25 0
      setgpio 26 1
      sleep 1
      setgpio 26 0
      echo "1" > /var/run/ircut
    ;;

    ir_cut_off)
      setgpio 26 0
      setgpio 25 1
      sleep 1
      setgpio 25 0
      echo "0" > /var/run/ircut
    ;;

    motor_left)
      /system/sdcard/bin/motor -d l -s $F_val

      # Waiting for the motor to run.
      SLEEP_NUM=$(awk -v a="$F_val" 'BEGIN{printf ("%f",a*1.3/1000)}')
      sleep ${SLEEP_NUM//-/}
      # Display AXIS to OSD
      update_axis
      /system/sdcard/bin/setconf -k o -v "$OSD"
    ;;

    motor_right)
      /system/sdcard/bin/motor -d r -s $F_val
      # Waiting for the motor to run.
      SLEEP_NUM=$(awk -v a="$F_val" 'BEGIN{printf ("%f",a*1.3/1000)}')
      sleep ${SLEEP_NUM//-/}
      # Display AXIS to OSD
      update_axis
      /system/sdcard/bin/setconf -k o -v "$OSD"
    ;;

    motor_up)
      /system/sdcard/bin/motor -d u -s $F_val
      # Waiting for the motor to run.
      SLEEP_NUM=$(awk -v a="$F_val" 'BEGIN{printf ("%f",a*1.3/1000)}')
      sleep ${SLEEP_NUM//-/}
      # Display AXIS to OSD
      update_axis
      /system/sdcard/bin/setconf -k o -v "$OSD"
    ;;

    motor_down)
      /system/sdcard/bin/motor -d d -s $F_val
      # Waiting for the motor to run.
      SLEEP_NUM=$(awk -v a="$F_val" 'BEGIN{printf ("%f",a*1.3/1000)}')
      sleep ${SLEEP_NUM//-/}
      # Display AXIS to OSD
      update_axis
      /system/sdcard/bin/setconf -k o -v "$OSD"
    ;;

    motor_vcalibrate)
      /system/sdcard/bin/motor -d v -s 100
    ;;

    motor_hcalibrate)
      /system/sdcard/bin/motor -d h -s 100
    ;;

    motor_calibrate)
      /system/sdcard/bin/motor -d h -s 100
      /system/sdcard/bin/motor -d v -s 100
    ;;
    
    motor_PTZ)
       /system/sdcard/scripts/PTZpresets.sh $F_x_axis $F_y_axis                        
    ;;

    audio_test)
          F_audioSource=$(printf '%b' "${F_audioSource//%/\\x}")
          if [ "$F_audioSource" == "" ]; then
              F_audioSource="/usr/share/notify/CN/init_ok.wav"
          fi
          /system/sdcard/bin/busybox nohup /system/sdcard/bin/audioplay $F_audioSource $F_audiotestVol >> "/var/log/update.log" &
          echo  "Play $F_audioSource at volume $F_audiotestVol"
          return
    ;;

    h264_start)
      /system/sdcard/controlscripts/rtsp-h264 start
    ;;

    h264_noseg_start)
      /system/sdcard/controlscripts/rtsp-h264 start
    ;;

    mjpeg_start)
      /system/sdcard/controlscripts/rtsp-mjpeg start
    ;;

    h264_nosegmentation_start)
      /system/sdcard/controlscripts/rtsp-h264 start
    ;;

    xiaomi_start)
      echo 1 > /sys/class/gpio/gpio39/value
      echo 39 > /sys/class/gpio/unexport
      killall v4l2rtspserver-master
      busybox insmod /driver/sinfo.ko  2>&1
      busybox rmmod sample_motor  2>&1
      /system/init/app_init.sh &
    ;;

    rtsp_stop)
      /system/sdcard/controlscripts/rtsp-mjpeg stop
      /system/sdcard/controlscripts/rtsp-h264 stop
    ;;

    settz)
       ntp_srv=$(printf '%b' "${F_ntp_srv//%/\\x}")
       #read ntp_serv.conf
       conf_ntp_srv=$(cat /system/sdcard/config/ntp_srv.conf)

      if [ $conf_ntp_srv != "$ntp_srv" ]; then
        echo "<p>Setting NTP Server to '$ntp_srv'...</p>"
        echo "$ntp_srv" > /system/sdcard/config/ntp_srv.conf
        echo "<p>Syncing time on '$ntp_srv'...</p>"
        if /system/sdcard/bin/busybox ntpd -q -n -p "$ntp_srv" > /dev/null 2>&1; then
          echo "<p>Success</p>"
        else
          echo "<p>Failed</p>"
        fi
      fi

      tz=$(printf '%b' "${F_tz//%/\\x}")
      if [ "$(cat /etc/TZ)" != "$tz" ]; then
        echo "<p>Setting TZ to '$tz'...</p>"
        echo "$tz" > /etc/TZ
        echo "<p>Syncing time...</p>"
        if /system/sdcard/bin/busybox ntpd -q -n -p "$ntp_srv" > /dev/null 2>&1; then
          echo "<p>Success</p>"
        else echo "<p>Failed</p>"
        fi
      fi
      hst=$(printf '%b' "${F_hostname//%/\\x}")
      if [ "$(cat /system/sdcard/config/hostname.conf)" != "$hst" ]; then
        echo "<p>Setting hostname to '$hst'...</p>"
        echo "$hst" > /system/sdcard/config/hostname.conf
        if hostname "$hst"; then
          echo "<p>Success</p>"
        else echo "<p>Failed</p>"
        fi
      fi
      return
    ;;

    set_http_password)
      password=$(printf '%b' "${F_password//%/\\x}")
      echo "<p>Setting http password to : $password</p>"
      http_password "$password"
    ;;

    osd)
      enabled=$(printf '%b' "${F_OSDenable}")
      axis_enable=$(printf '%b' "${F_AXISenable}")
      position=$(printf '%b' "${F_Position}")
      osdtext=$(printf '%b' "${F_osdtext//%/\\x}")
      osdtext=$(echo "$osdtext" | sed -e "s/\\+/ /g")

      if [ ! -z "$axis_enable" ];then
        update_axis
        osdtext="${osdtext} ${AXIS}"
        echo "DISPLAY_AXIS=true" > /system/sdcard/config/osd.conf
        echo DISPLAY_AXIS enable
      else
        echo "DISPLAY_AXIS=false" > /system/sdcard/config/osd.conf
        echo DISPLAY_AXIS disable
      fi

      if [ ! -z "$enabled" ]; then
        /system/sdcard/bin/setconf -k o -v "$osdtext"
        echo "OSD=\"${osdtext}\"" | sed -r 's/[ ]X=.*"/"/' >> /system/sdcard/config/osd.conf
        echo "OSD set"
      else
        echo "OSD removed"
        /system/sdcard/bin/setconf -k o -v ""
        echo "OSD=\"\" " >> /system/sdcard/config/osd.conf
      fi

      echo "COLOR=${F_color}" >> /system/sdcard/config/osd.conf
      /system/sdcard/bin/setconf -k c -v "${F_color}"

      echo "SIZE=${F_size}" >> /system/sdcard/config/osd.conf
      /system/sdcard/bin/setconf -k s -v "${F_size}"

      echo "POSY=${F_posy}" >> /system/sdcard/config/osd.conf
      /system/sdcard/bin/setconf -k x -v "${F_posy}"

      echo "FIXEDW=${F_fixedw}" >> /system/sdcard/config/osd.conf
      /system/sdcard/bin/setconf -k w -v "${F_fixedw}"

      echo "SPACE=${F_spacepixels}" >> /system/sdcard/config/osd.conf
      /system/sdcard/bin/setconf -k p -v "${F_spacepixels}"
      return
    ;;

    setldravg)
      ldravg=$(printf '%b' "${F_avg/%/\\x}")
      ldravg=$(echo "$ldravg" | sed "s/[^0-9]//g")
      echo AVG="$ldravg" > /system/sdcard/config/ldr-average.conf
      echo "Average set to $ldravg iterations."
      return
    ;;

    auto_night_mode_start)
      /system/sdcard/controlscripts/auto-night-detection start
    ;;

    auto_night_mode_stop)
      /system/sdcard/controlscripts/auto-night-detection stop
    ;;

    toggle-rtsp-nightvision-on)
      /system/sdcard/bin/setconf -k n -v 1
    ;;

    toggle-rtsp-nightvision-off)
      /system/sdcard/bin/setconf -k n -v 0
    ;;

    flip-on)
      /system/sdcard/bin/setconf -k f -v 1
    ;;

    flip-off)
      /system/sdcard/bin/setconf -k f -v 0
    ;;

    motion_detection_on)
        motion_sensitivity=4
        if [ -f /system/sdcard/config/motion.conf ]; then
            source /system/sdcard/config/motion.conf
        fi
        if [ $motion_sensitivity -eq -1 ]; then
             motion_sensitivity=4
        fi
        /system/sdcard/bin/setconf -k m -v $motion_sensitivity
        rewrite_config /system/sdcard/config/motion.conf motion_sensitivity $motion_sensitivity
    ;;

    motion_detection_off)
      /system/sdcard/bin/setconf -k m -v -1
    ;;

    set_video_size)
      video_size=$(echo "${F_video_size}"| sed -e 's/+/ /g')
      video_format=$(printf '%b' "${F_video_format/%/\\x}")
      brbitrate=$(printf '%b' "${F_brbitrate/%/\\x}")
      videopassword=$(printf '%b' "${F_videopassword//%/\\x}")
      videouser=$(printf '%b' "${F_videouser//%/\\x}")
      videoport=$(echo "${F_videoport}"| sed -e 's/+/ /g')
      frmRateDen=$(printf '%b' "${F_frmRateDen/%/\\x}")
      frmRateNum=$(printf '%b' "${F_frmRateNum/%/\\x}")

      rewrite_config /system/sdcard/config/rtspserver.conf RTSPH264OPTS "\"$video_size\""
      rewrite_config /system/sdcard/config/rtspserver.conf RTSPMJPEGOPTS "\"$video_size\""
      rewrite_config /system/sdcard/config/rtspserver.conf BITRATE "$brbitrate"
      rewrite_config /system/sdcard/config/rtspserver.conf VIDEOFORMAT "$video_format"
      rewrite_config /system/sdcard/config/rtspserver.conf USERNAME "$videouser"
      rewrite_config /system/sdcard/config/rtspserver.conf USERPASSWORD "$videopassword"
      rewrite_config /system/sdcard/config/rtspserver.conf PORT "$videoport"
      if [ "$frmRateDen" != "" ]; then
        rewrite_config /system/sdcard/config/rtspserver.conf FRAMERATE_DEN "$frmRateDen"
      fi
      if [ "$frmRateNum" != "" ]; then
          rewrite_config /system/sdcard/config/rtspserver.conf FRAMERATE_NUM "$frmRateNum"
      fi

      echo "Video resolution set to $video_size<br/>"
      echo "Bitrate set to $brbitrate<br/>"
      echo "FrameRate set to $frmRateDen/$frmRateNum <br/>"
      /system/sdcard/bin/setconf -k d -v "$frmRateNum,$frmRateDen" 2>/dev/null
      echo "Video format set to $video_format<br/>"

      if [ "$(rtsp_h264_server status)" = "ON" ]; then
        rtsp_h264_server off
        rtsp_h264_server on
      fi
      if [ "$(rtsp_mjpeg_server status)" = "ON" ]; then
        rtsp_mjpeg_server off
        rtsp_mjpeg_server on
      fi
      return
    ;;

    set_region_of_interest)
        rewrite_config /system/sdcard/config/motion.conf region_of_interest "${F_x0},${F_y0},${F_x1},${F_y1}"
        rewrite_config /system/sdcard/config/motion.conf motion_sensitivity "${F_motion_sensitivity}"
        rewrite_config /system/sdcard/config/motion.conf motion_indicator_color "${F_motion_indicator_color}"
        rewrite_config /system/sdcard/config/motion.conf motion_timeout "${F_motion_timeout}"
        if [ "${F_motion_tracking}X" == "X" ]
        then
            rewrite_config /system/sdcard/config/motion.conf motion_tracking off
             /system/sdcard/bin/setconf -k t -v off
        else
            rewrite_config /system/sdcard/config/motion.conf motion_tracking on
            /system/sdcard/bin/setconf -k t -v on
        fi

        /system/sdcard/bin/setconf -k r -v ${F_x0},${F_y0},${F_x1},${F_y1}
        /system/sdcard/bin/setconf -k m -v ${F_motion_sensitivity}
        /system/sdcard/bin/setconf -k z -v ${F_motion_indicator_color}
        /system/sdcard/bin/setconf -k u -v ${F_motion_timeout}

        # Changed the detection region, need to restart the server
        if [ ${F_restart_server} == "1" ]
        then
            if [ "$(rtsp_h264_server status)" == "ON" ]; then
                rtsp_h264_server off
                rtsp_h264_server on
            fi
            if [ "$(rtsp_mjpeg_server status)" == "ON" ]; then
                rtsp_mjpeg_server off
                rtsp_mjpeg_server on
            fi
        fi

        echo "Motion Configuration done"
        return
    ;;
    offDebug)
        /system/sdcard/controlscripts/debug-on-osd stop

    ;;
    onDebug)
        /system/sdcard/controlscripts/debug-on-osd start
    ;;

    conf_timelapse)
      tlinterval=$(printf '%b' "${F_tlinterval/%/\\x}")
      tlinterval=$(echo "$tlinterval" | sed "s/[^0-9\.]//g")
      if [ "$tlinterval" ]; then
        rewrite_config /system/sdcard/config/timelapse.conf TIMELAPSE_INTERVAL "$tlinterval"
        echo "Timelapse interval set to $tlinterval seconds."
      else
        echo "Invalid timelapse interval"
      fi
      tlduration=$(printf '%b' "${F_tlduration/%/\\x}")
      tlduration=$(echo "$tlduration" | sed "s/[^0-9\.]//g")
      if [ "$tlduration" ]; then
        rewrite_config /system/sdcard/config/timelapse.conf TIMELAPSE_DURATION "$tlduration"
        echo "Timelapse duration set to $tlduration minutes."
      else
        echo "Invalid timelapse duration"
      fi
      return
    ;;
    conf_audioin)

       audioinFormat=$(printf '%b' "${F_audioinFormat/%/\\x}")
       audioinBR=$(printf '%b' "${F_audioinBR/%/\\x}")
       audiooutBR=$(printf '%b' "${F_audiooutBR/%/\\x}")

       if [ "$audioinBR" == "" ]; then
            audioinBR="8000"
       fi
       if [ "$audiooutBR" == "" ]; then
           audioOutBR = audioinBR
       fi
       if [ "$audioinFormat" == "OPUS" ]; then
            audioOutBR="48000"
       fi
       if [ "$audioinFormat" == "PCM" ]; then
            audioOutBR = audioinBR
       fi
       if [ "$audioinFormat" == "PCMU" ]; then
           audioOutBR = audioinBR
       fi

       rewrite_config /system/sdcard/config/rtspserver.conf AUDIOFORMAT "$audioinFormat"
       rewrite_config /system/sdcard/config/rtspserver.conf AUDIOINBR "$audioinBR"
       rewrite_config /system/sdcard/config/rtspserver.conf AUDIOOUTBR "$audiooutBR"
       rewrite_config /system/sdcard/config/rtspserver.conf FILTER "$F_audioinFilter"
       rewrite_config /system/sdcard/config/rtspserver.conf HIGHPASSFILTER "$F_HFEnabled"
       rewrite_config /system/sdcard/config/rtspserver.conf AECFILTER "$F_AECEnabled"
        rewrite_config /system/sdcard/config/rtspserver.conf HWVOLUME "$F_audioinVol"
       rewrite_config /system/sdcard/config/rtspserver.conf SWVOLUME "-1"


       echo "Audio format $audioinFormat <BR>"
       echo "In audio bitrate $audioinBR <BR>"
       echo "Out audio bitrate $audiooutBR <BR>"
       echo "Filter $F_audioinFilter <BR>"
       echo "High Pass Filter $F_HFEnabled <BR>"
       echo "AEC Filter $F_AECEnabled <BR>"
       echo  "Volume $F_audioinVol <BR>"
       /system/sdcard/bin/setconf -k q -v "$F_audioinFilter" 2>/dev/null
       /system/sdcard/bin/setconf -k l -v "$F_HFEnabled" 2>/dev/null
       /system/sdcard/bin/setconf -k a -v "$F_AECEnabled" 2>/dev/null
       /system/sdcard/bin/setconf -k h -v "$F_audioinVol" 2>/dev/null
       return
     ;;
     update)
        processId=$(ps | grep autoupdate.sh | grep -v grep)
        if [ "$processId" == "" ]
        then
            echo "===============" >> /system/sdcard/log/update.log
            date >> /var/log/update.log
            if [ "$F_login" != "" ]; then
                /system/sdcard/bin/busybox nohup /system/sdcard/autoupdate.sh -s -v -f -u $F_login  >> "/system/sdcard/log/update.log" &
            else
                /system/sdcard/bin/busybox nohup /system/sdcard/autoupdate.sh -s -v -f >> "/system/sdcard/log/update.log" &
            fi
            processId=$(ps | grep autoupdate.sh | grep -v grep)
        fi
        echo $processId
        return
      ;;
     show_updateProgress)
        processId=$(ps | grep autoupdate.sh | grep -v grep)
        if [ "$processId" == "" ]
        then
            echo -n -1
        else
            if [ -f /tmp/progress ] ; then
                cat /tmp/progress
            else
                echo -n 0
            fi
        fi
        return
        ;;
     motion_detection_mail_on)
         rewrite_config /system/sdcard/config/motion.conf sendemail "true"
         return
         ;;
     motion_detection_mail_off)
          rewrite_config /system/sdcard/config/motion.conf sendemail "false"
          return
          ;;
     motion_detection_led_on)
          rewrite_config /system/sdcard/config/motion.conf motion_trigger_led "true"
          return
          ;;
     motion_detection_led_off)
          rewrite_config /system/sdcard/config/motion.conf motion_trigger_led "false"
          return
          ;;
     motion_detection_snapshot_on)
          rewrite_config /system/sdcard/config/motion.conf save_snapshot "true"
          return
          ;;
     motion_detection_snapshot_off)
          rewrite_config /system/sdcard/config/motion.conf save_snapshot "false"
          return
          ;;
     motion_detection_mqtt_on)
          rewrite_config /system/sdcard/config/motion.conf publish_mqtt_message "true"
          return
          ;;
     motion_detection_mqtt_off)
          rewrite_config /system/sdcard/config/motion.conf publish_mqtt_message "false"
          return
          ;;

     *)
        echo "Unsupported command '$F_cmd'"
        ;;

  esac
fi

echo "<hr/>"
echo "<button title='Return to status page' onClick=\"window.location.href='status.cgi'\">Back</button>"
