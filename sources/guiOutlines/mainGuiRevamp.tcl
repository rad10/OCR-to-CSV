#############################################################################
# Generated by PAGE version 4.26
#  in conjunction with Tcl version 8.6
#  Mar 31, 2020 10:57:23 PM EDT  platform: Windows NT
set vTcl(timestamp) ""


if {!$vTcl(borrow) && !$vTcl(template)} {

set vTcl(actual_gui_bg) #d9d9d9
set vTcl(actual_gui_fg) #000000
set vTcl(actual_gui_analog) #ececec
set vTcl(actual_gui_menu_analog) #ececec
set vTcl(actual_gui_menu_bg) #d9d9d9
set vTcl(actual_gui_menu_fg) #000000
set vTcl(complement_color) #d9d9d9
set vTcl(analog_color_p) #d9d9d9
set vTcl(analog_color_m) #ececec
set vTcl(active_fg) #000000
set vTcl(actual_gui_menu_active_bg)  #ececec
set vTcl(active_menu_fg) #000000
}




proc vTclWindow.top42 {base} {
    global vTcl
    if {$base == ""} {
        set base .top42
    }
    if {[winfo exists $base]} {
        wm deiconify $base; return
    }
    set top $base
    ###################
    # CREATING WIDGETS
    ###################
    vTcl::widgets::core::toplevel::createCmd $top -class Toplevel \
        -menu {{}} -background $vTcl(actual_gui_bg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black 
    wm focusmodel $top passive
    wm geometry $top 600x450+401+150
    update
    # set in toplevel.wgt.
    global vTcl
    global img_list
    set vTcl(save,dflt,origin) 0
    wm maxsize $top 1370 749
    wm minsize $top 120 1
    wm overrideredirect $top 0
    wm resizable $top 1 1
    wm deiconify $top
    wm title $top "New Toplevel"
    vTcl:DefineAlias "$top" "Toplevel1" vTcl:Toplevel:WidgetProc "" 1
    button $top.but43 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background $vTcl(actual_gui_bg) -disabledforeground #a3a3a3 \
        -font TkDefaultFont -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -pady 0 -text {Select Signin sheet} 
    vTcl:DefineAlias "$top.but43" "inputSheet" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.but43
    button $top.but44 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background $vTcl(actual_gui_bg) -disabledforeground #a3a3a3 \
        -font TkDefaultFont -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -pady 0 -text {Select output csv} 
    vTcl:DefineAlias "$top.but44" "outputCSV" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.but44
    label $top.lab45 \
        -activebackground #f9f9f9 -activeforeground black -background #e6e6e6 \
        -disabledforeground #a3a3a3 -font TkDefaultFont \
        -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -text Label 
    vTcl:DefineAlias "$top.lab45" "imagePortrait" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.lab45
    label $top.lab46 \
        -activebackground #f9f9f9 -activeforeground black -background #e1e1e1 \
        -disabledforeground #a3a3a3 -font TkDefaultFont -foreground #ff0000 \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -text {Uh oh. It looks like we couldnt condifently decide who or what this is. We need you to either confirm our guess or type in the correct value} 
    vTcl:DefineAlias "$top.lab46" "errorLabel" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.lab46
    entry $top.ent47 \
        -background white -disabledforeground #a3a3a3 -font TkFixedFont \
        -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -insertbackground black -selectbackground #c4c4c4 \
        -selectforeground black 
    vTcl:DefineAlias "$top.ent47" "correctionEntry" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.ent47
    button $top.but45 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background $vTcl(actual_gui_bg) -disabledforeground #a3a3a3 \
        -font TkDefaultFont -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -pady 0 -text Button 
    vTcl:DefineAlias "$top.but45" "AIGuess" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.but45
    button $top.but46 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background $vTcl(actual_gui_bg) -disabledforeground #a3a3a3 \
        -font TkDefaultFont -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -pady 0 -text Submit 
    vTcl:DefineAlias "$top.but46" "submit" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.but46
    label $top.lab47 \
        -activebackground #f9f9f9 -activeforeground black \
        -background $vTcl(actual_gui_bg) -disabledforeground #a3a3a3 \
        -font TkDefaultFont -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -justify right -text {Were not confident, but is it:} 
    vTcl:DefineAlias "$top.lab47" "confidenceDescription" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.lab47
    label $top.lab48 \
        -activebackground #f9f9f9 -activeforeground black \
        -background $vTcl(actual_gui_bg) -disabledforeground #a3a3a3 \
        -font TkDefaultFont -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -text Or 
    vTcl:DefineAlias "$top.lab48" "orLabel" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.lab48
    ttk::progressbar $top.tPr49
    vTcl:DefineAlias "$top.tPr49" "TranslationProgress" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.tPr49
    label $top.lab50 \
        -activebackground #f9f9f9 -activeforeground black -anchor w \
        -background $vTcl(actual_gui_bg) -disabledforeground #a3a3a3 \
        -font TkDefaultFont -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -text {Sheet: x of y} 
    vTcl:DefineAlias "$top.lab50" "SheetStatus" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.lab50
    button $top.but47 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background #17a252 -disabledforeground #a3a3a3 -font TkDefaultFont \
        -foreground #ffffff -highlightbackground $vTcl(actual_gui_bg) \
        -highlightcolor black -pady 0 -text Start 
    vTcl:DefineAlias "$top.but47" "start" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.but47
    label $top.lab43 \
        -anchor w -background $vTcl(actual_gui_bg) \
        -disabledforeground #a3a3a3 -font TkDefaultFont \
        -foreground $vTcl(actual_gui_fg) -text Version 
    vTcl:DefineAlias "$top.lab43" "version" vTcl:WidgetProc "Toplevel1" 1
    vTcl:copy_lock $top.lab43
    ###################
    # SETTING GEOMETRY
    ###################
    place $top.but43 \
        -in $top -x 20 -y 20 -width 157 -relwidth 0 -height 34 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.but44 \
        -in $top -x 20 -y 70 -width 157 -relwidth 0 -height 34 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.lab45 \
        -in $top -x 250 -y 10 -width 314 -relwidth 0 -height 221 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.lab46 \
        -in $top -x 10 -y 160 -width 224 -relwidth 0 -height 71 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.ent47 \
        -in $top -x 80 -y 310 -width 334 -relwidth 0 -height 30 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.but45 \
        -in $top -x 330 -y 250 -width 227 -relwidth 0 -height 34 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.but46 \
        -in $top -x 430 -y 310 -width 127 -relwidth 0 -height 34 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.lab47 \
        -in $top -x 160 -y 250 -width 164 -relwidth 0 -height 31 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.lab48 \
        -in $top -x 10 -y 310 -width 64 -relwidth 0 -height 31 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.tPr49 \
        -in $top -x 10 -y 410 -width 570 -relwidth 0 -height 22 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.lab50 \
        -in $top -x 20 -y 380 -width 554 -relwidth 0 -height 21 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.but47 \
        -in $top -x 20 -y 115 -width 157 -relwidth 0 -height 34 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.lab43 \
        -in $top -x 20 -y 360 -width 134 -relwidth 0 -height 21 -relheight 0 \
        -anchor nw -bordermode ignore 

    vTcl:FireEvent $base <<Ready>>
}

set btop ""
if {$vTcl(borrow)} {
    set btop .bor[expr int([expr rand() * 100])]
    while {[lsearch $btop $vTcl(tops)] != -1} {
        set btop .bor[expr int([expr rand() * 100])]
    }
}
set vTcl(btop) $btop
Window show .
Window show .top42 $btop
if {$vTcl(borrow)} {
    $btop configure -background plum
}

