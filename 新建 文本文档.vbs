Dim userInput

Do
    userInput = InputBox("叫爸爸", "快叫爸爸")
    If userInput = "爸爸" Then
        MsgBox "诶,乖儿子", vbInformation, "对了!"
        Exit Do  ' 退出循环
    End If
Loop
