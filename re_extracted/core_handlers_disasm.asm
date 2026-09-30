; =====================================================================
; DIGITAL WORKS (Delphi 5) - DISASSEMBLY OF CORE EVENT HANDLERS (x86)
; =====================================================================

; ---------------------------------------------------------------------
; Handler: RunCircuit (0x0049dabc - 0x0049db78)
; ---------------------------------------------------------------------
  49dabc:	53                   	push   ebx
  49dabd:	83 c4 f8             	add    esp,0xfffffff8
  49dac0:	8b d8                	mov    ebx,eax
  49dac2:	8b 83 30 05 00 00    	mov    eax,DWORD PTR [ebx+0x530]
  49dac8:	80 b8 2a 01 00 00 00 	cmp    BYTE PTR [eax+0x12a],0x0
  49dacf:	0f 84 9f 00 00 00    	je     0x49db74
  49dad5:	8b 83 38 05 00 00    	mov    eax,DWORD PTR [ebx+0x538]
  49dadb:	80 b8 2a 01 00 00 00 	cmp    BYTE PTR [eax+0x12a],0x0
  49dae2:	0f 85 8c 00 00 00    	jne    0x49db74
  49dae8:	8b d4                	mov    edx,esp
  49daea:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49daf0:	e8 8f 83 fe ff       	call   0x485e84
  49daf5:	80 7c 24 06 00       	cmp    BYTE PTR [esp+0x6],0x0
  49dafa:	74 0f                	je     0x49db0b
  49dafc:	33 d2                	xor    edx,edx
  49dafe:	8b 83 30 05 00 00    	mov    eax,DWORD PTR [ebx+0x530]
  49db04:	e8 57 a7 fd ff       	call   0x478260
  49db09:	eb 2a                	jmp    0x49db35
  49db0b:	80 7c 24 04 00       	cmp    BYTE PTR [esp+0x4],0x0
  49db10:	74 0f                	je     0x49db21
  49db12:	33 d2                	xor    edx,edx
  49db14:	8b 83 30 05 00 00    	mov    eax,DWORD PTR [ebx+0x530]
  49db1a:	e8 41 a7 fd ff       	call   0x478260
  49db1f:	eb 14                	jmp    0x49db35
  49db21:	80 7c 24 07 00       	cmp    BYTE PTR [esp+0x7],0x0
  49db26:	74 0d                	je     0x49db35
  49db28:	33 d2                	xor    edx,edx
  49db2a:	8b 83 30 05 00 00    	mov    eax,DWORD PTR [ebx+0x530]
  49db30:	e8 2b a7 fd ff       	call   0x478260
  49db35:	a1 c8 31 4a 00       	mov    eax,ds:0x4a31c8
  49db3a:	8b 00                	mov    eax,DWORD PTR [eax]
  49db3c:	80 78 47 00          	cmp    BYTE PTR [eax+0x47],0x0
  49db40:	74 0c                	je     0x49db4e
  49db42:	a1 c8 31 4a 00       	mov    eax,ds:0x4a31c8
  49db47:	8b 00                	mov    eax,DWORD PTR [eax]
  49db49:	e8 ba 32 00 00       	call   0x4a0e08
  49db4e:	a1 c8 31 4a 00       	mov    eax,ds:0x4a31c8
  49db53:	8b 00                	mov    eax,DWORD PTR [eax]
  49db55:	ff 80 48 03 00 00    	inc    DWORD PTR [eax+0x348]
  49db5b:	a1 bc 2f 4a 00       	mov    eax,ds:0x4a2fbc
  49db60:	8b 00                	mov    eax,DWORD PTR [eax]
  49db62:	80 78 47 00          	cmp    BYTE PTR [eax+0x47],0x0
  49db66:	74 0c                	je     0x49db74
  49db68:	a1 bc 2f 4a 00       	mov    eax,ds:0x4a2fbc
  49db6d:	8b 00                	mov    eax,DWORD PTR [eax]
  49db6f:	e8 08 74 ff ff       	call   0x494f7c
  49db74:	59                   	pop    ecx
  49db75:	5a                   	pop    edx
  49db76:	5b                   	pop    ebx
  49db77:	c3                   	ret

; ---------------------------------------------------------------------
; Handler: SpeedRunClick (0x0049db78 - 0x0049dbfc)
; ---------------------------------------------------------------------
  49db78:	53                   	push   ebx
  49db79:	8b d8                	mov    ebx,eax
  49db7b:	8b 83 30 05 00 00    	mov    eax,DWORD PTR [ebx+0x530]
  49db81:	8b 10                	mov    edx,DWORD PTR [eax]
  49db83:	ff 92 80 00 00 00    	call   DWORD PTR [edx+0x80]
  49db89:	8b 83 30 05 00 00    	mov    eax,DWORD PTR [ebx+0x530]
  49db8f:	8a 90 2a 01 00 00    	mov    dl,BYTE PTR [eax+0x12a]
  49db95:	8b 83 dc 02 00 00    	mov    eax,DWORD PTR [ebx+0x2dc]
  49db9b:	e8 10 16 fb ff       	call   0x44f1b0
  49dba0:	8b 83 30 05 00 00    	mov    eax,DWORD PTR [ebx+0x530]
  49dba6:	8a 90 2a 01 00 00    	mov    dl,BYTE PTR [eax+0x12a]
  49dbac:	a1 c8 31 4a 00       	mov    eax,ds:0x4a31c8
  49dbb1:	8b 00                	mov    eax,DWORD PTR [eax]
  49dbb3:	8b 80 10 03 00 00    	mov    eax,DWORD PTR [eax+0x310]
  49dbb9:	e8 a2 a6 fd ff       	call   0x478260
  49dbbe:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49dbc4:	e8 f7 87 fe ff       	call   0x4863c0
  49dbc9:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49dbcf:	e8 44 85 fe ff       	call   0x486118
  49dbd4:	a1 c8 31 4a 00       	mov    eax,ds:0x4a31c8
  49dbd9:	8b 00                	mov    eax,DWORD PTR [eax]
  49dbdb:	8b 90 50 03 00 00    	mov    edx,DWORD PTR [eax+0x350]
  49dbe1:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49dbe7:	e8 20 88 fe ff       	call   0x48640c
  49dbec:	a1 c8 31 4a 00       	mov    eax,ds:0x4a31c8
  49dbf1:	8b 00                	mov    eax,DWORD PTR [eax]
  49dbf3:	e8 fc 39 00 00       	call   0x4a15f4
  49dbf8:	5b                   	pop    ebx
  49dbf9:	c3                   	ret
  49dbfa:	8b c0                	mov    eax,eax

; ---------------------------------------------------------------------
; Handler: SpeedStopClick (0x0049dbfc - 0x0049dc20)
; ---------------------------------------------------------------------
  49dbfc:	33 d2                	xor    edx,edx
  49dbfe:	8b 80 30 05 00 00    	mov    eax,DWORD PTR [eax+0x530]
  49dc04:	e8 57 a6 fd ff       	call   0x478260
  49dc09:	a1 c8 31 4a 00       	mov    eax,ds:0x4a31c8
  49dc0e:	8b 00                	mov    eax,DWORD PTR [eax]
  49dc10:	8b 80 10 03 00 00    	mov    eax,DWORD PTR [eax+0x310]
  49dc16:	33 d2                	xor    edx,edx
  49dc18:	e8 43 a6 fd ff       	call   0x478260
  49dc1d:	c3                   	ret
  49dc1e:	8b c0                	mov    eax,eax

; ---------------------------------------------------------------------
; Handler: SpeedStepClick (0x0049da40 - 0x0049dabc)
; ---------------------------------------------------------------------
  49da40:	53                   	push   ebx
  49da41:	83 c4 f8             	add    esp,0xfffffff8
  49da44:	8b d8                	mov    ebx,eax
  49da46:	80 bb e8 05 00 00 00 	cmp    BYTE PTR [ebx+0x5e8],0x0
  49da4d:	74 0f                	je     0x49da5e
  49da4f:	8b d4                	mov    edx,esp
  49da51:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49da57:	e8 28 84 fe ff       	call   0x485e84
  49da5c:	eb 1a                	jmp    0x49da78
  49da5e:	8b d4                	mov    edx,esp
  49da60:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49da66:	e8 19 84 fe ff       	call   0x485e84
  49da6b:	8b d4                	mov    edx,esp
  49da6d:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49da73:	e8 0c 84 fe ff       	call   0x485e84
  49da78:	a1 c8 31 4a 00       	mov    eax,ds:0x4a31c8
  49da7d:	8b 00                	mov    eax,DWORD PTR [eax]
  49da7f:	80 78 47 00          	cmp    BYTE PTR [eax+0x47],0x0
  49da83:	74 0c                	je     0x49da91
  49da85:	a1 c8 31 4a 00       	mov    eax,ds:0x4a31c8
  49da8a:	8b 00                	mov    eax,DWORD PTR [eax]
  49da8c:	e8 77 33 00 00       	call   0x4a0e08
  49da91:	a1 bc 2f 4a 00       	mov    eax,ds:0x4a2fbc
  49da96:	8b 00                	mov    eax,DWORD PTR [eax]
  49da98:	80 78 47 00          	cmp    BYTE PTR [eax+0x47],0x0
  49da9c:	74 0c                	je     0x49daaa
  49da9e:	a1 bc 2f 4a 00       	mov    eax,ds:0x4a2fbc
  49daa3:	8b 00                	mov    eax,DWORD PTR [eax]
  49daa5:	e8 d2 74 ff ff       	call   0x494f7c
  49daaa:	a1 c8 31 4a 00       	mov    eax,ds:0x4a31c8
  49daaf:	8b 00                	mov    eax,DWORD PTR [eax]
  49dab1:	ff 80 48 03 00 00    	inc    DWORD PTR [eax+0x348]
  49dab7:	59                   	pop    ecx
  49dab8:	5a                   	pop    edx
  49dab9:	5b                   	pop    ebx
  49daba:	c3                   	ret
  49dabb:	90                   	nop

; ---------------------------------------------------------------------
; Handler: DeleteClick (0x0049d5c4 - 0x0049d600)
; ---------------------------------------------------------------------
  49d5c4:	55                   	push   ebp
  49d5c5:	8b ec                	mov    ebp,esp
  49d5c7:	6a 00                	push   0x0
  49d5c9:	53                   	push   ebx
  49d5ca:	8b d8                	mov    ebx,eax
  49d5cc:	33 c0                	xor    eax,eax
  49d5ce:	55                   	push   ebp
  49d5cf:	68 00 d7 49 00       	push   0x49d700
  49d5d4:	64 ff 30             	push   DWORD PTR fs:[eax]
  49d5d7:	64 89 20             	mov    DWORD PTR fs:[eax],esp
  49d5da:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49d5e0:	8b 80 78 02 00 00    	mov    eax,DWORD PTR [eax+0x278]
  49d5e6:	e8 49 af fb ff       	call   0x458534
  49d5eb:	85 c0                	test   eax,eax
  49d5ed:	0f 84 d4 00 00 00    	je     0x49d6c7
  49d5f3:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49d5f9:	8b 80 78 02 00 00    	mov    eax,DWORD PTR [eax+0x278]
  49d5ff:	e8                   	.byte 0xe8

; ---------------------------------------------------------------------
; Handler: FormKeyDown (0x0049f394 - 0x0049f480)
; ---------------------------------------------------------------------
  49f394:	55                   	push   ebp
  49f395:	8b ec                	mov    ebp,esp
  49f397:	6a 00                	push   0x0
  49f399:	6a 00                	push   0x0
  49f39b:	6a 00                	push   0x0
  49f39d:	6a 00                	push   0x0
  49f39f:	6a 00                	push   0x0
  49f3a1:	6a 00                	push   0x0
  49f3a3:	53                   	push   ebx
  49f3a4:	56                   	push   esi
  49f3a5:	8b f1                	mov    esi,ecx
  49f3a7:	8b d8                	mov    ebx,eax
  49f3a9:	33 c0                	xor    eax,eax
  49f3ab:	55                   	push   ebp
  49f3ac:	68 a3 f5 49 00       	push   0x49f5a3
  49f3b1:	64 ff 30             	push   DWORD PTR fs:[eax]
  49f3b4:	64 89 20             	mov    DWORD PTR fs:[eax],esp
  49f3b7:	66 83 3e 25          	cmp    WORD PTR [esi],0x25
  49f3bb:	75 18                	jne    0x49f3d5
  49f3bd:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49f3c3:	8b 80 78 02 00 00    	mov    eax,DWORD PTR [eax+0x278]
  49f3c9:	33 c9                	xor    ecx,ecx
  49f3cb:	83 ca ff             	or     edx,0xffffffff
  49f3ce:	e8 51 a7 fb ff       	call   0x459b24
  49f3d3:	eb 5c                	jmp    0x49f431
  49f3d5:	66 83 3e 26          	cmp    WORD PTR [esi],0x26
  49f3d9:	75 18                	jne    0x49f3f3
  49f3db:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49f3e1:	8b 80 78 02 00 00    	mov    eax,DWORD PTR [eax+0x278]
  49f3e7:	83 c9 ff             	or     ecx,0xffffffff
  49f3ea:	33 d2                	xor    edx,edx
  49f3ec:	e8 33 a7 fb ff       	call   0x459b24
  49f3f1:	eb 3e                	jmp    0x49f431
  49f3f3:	66 83 3e 27          	cmp    WORD PTR [esi],0x27
  49f3f7:	75 1a                	jne    0x49f413
  49f3f9:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49f3ff:	8b 80 78 02 00 00    	mov    eax,DWORD PTR [eax+0x278]
  49f405:	33 c9                	xor    ecx,ecx
  49f407:	ba 01 00 00 00       	mov    edx,0x1
  49f40c:	e8 13 a7 fb ff       	call   0x459b24
  49f411:	eb 1e                	jmp    0x49f431
  49f413:	66 83 3e 28          	cmp    WORD PTR [esi],0x28
  49f417:	75 18                	jne    0x49f431
  49f419:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49f41f:	8b 80 78 02 00 00    	mov    eax,DWORD PTR [eax+0x278]
  49f425:	b9 01 00 00 00       	mov    ecx,0x1
  49f42a:	33 d2                	xor    edx,edx
  49f42c:	e8 f3 a6 fb ff       	call   0x459b24
  49f431:	66 83 3e 70          	cmp    WORD PTR [esi],0x70
  49f435:	0f 85 4d 01 00 00    	jne    0x49f588
  49f43b:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49f441:	8b 80 78 02 00 00    	mov    eax,DWORD PTR [eax+0x278]
  49f447:	e8 e8 90 fb ff       	call   0x458534
  49f44c:	85 c0                	test   eax,eax
  49f44e:	0f 84 1b 01 00 00    	je     0x49f56f
  49f454:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49f45a:	8b 80 78 02 00 00    	mov    eax,DWORD PTR [eax+0x278]
  49f460:	e8 cf 90 fb ff       	call   0x458534
  49f465:	8b 15 f8 22 46 00    	mov    edx,DWORD PTR ds:0x4622f8
  49f46b:	e8 a4 3c f6 ff       	call   0x403114
  49f470:	84 c0                	test   al,al
  49f472:	74 36                	je     0x49f4aa
  49f474:	8b 83 e4 05 00 00    	mov    eax,DWORD PTR [ebx+0x5e4]
  49f47a:	8b 80 78 02 00 00    	mov    eax,DWORD PTR [eax+0x278]

; ---------------------------------------------------------------------
; Handler: FormShortCut (0x0049f2a4 - 0x0049f394)
; ---------------------------------------------------------------------
  49f2a4:	53                   	push   ebx
  49f2a5:	56                   	push   esi
  49f2a6:	57                   	push   edi
  49f2a7:	55                   	push   ebp
  49f2a8:	8b e9                	mov    ebp,ecx
  49f2aa:	8b fa                	mov    edi,edx
  49f2ac:	8b f0                	mov    esi,eax
  49f2ae:	8b 96 e4 05 00 00    	mov    edx,DWORD PTR [esi+0x5e4]
  49f2b4:	80 ba 98 02 00 00 00 	cmp    BYTE PTR [edx+0x298],0x0
  49f2bb:	74 2f                	je     0x49f2ec
  49f2bd:	66 8b 47 04          	mov    ax,WORD PTR [edi+0x4]
  49f2c1:	66 83 f8 2e          	cmp    ax,0x2e
  49f2c5:	74 06                	je     0x49f2cd
  49f2c7:	66 83 f8 1b          	cmp    ax,0x1b
  49f2cb:	75 1f                	jne    0x49f2ec
  49f2cd:	33 d2                	xor    edx,edx
  49f2cf:	8b 86 e4 05 00 00    	mov    eax,DWORD PTR [esi+0x5e4]
  49f2d5:	e8 3e 62 fe ff       	call   0x485518
  49f2da:	b2 01                	mov    dl,0x1
  49f2dc:	8b 86 e4 05 00 00    	mov    eax,DWORD PTR [esi+0x5e4]
  49f2e2:	e8 31 62 fe ff       	call   0x485518
  49f2e7:	e9 a3 00 00 00       	jmp    0x49f38f
  49f2ec:	8b d7                	mov    edx,edi
  49f2ee:	8b 86 a0 03 00 00    	mov    eax,DWORD PTR [esi+0x3a0]
  49f2f4:	66 bb f0 ff          	mov    bx,0xfff0
  49f2f8:	e8 7b 3e f6 ff       	call   0x403178
  49f2fd:	84 c0                	test   al,al
  49f2ff:	74 09                	je     0x49f30a
  49f301:	c6 45 00 01          	mov    BYTE PTR [ebp+0x0],0x1
  49f305:	e9 85 00 00 00       	jmp    0x49f38f
  49f30a:	8b d7                	mov    edx,edi
  49f30c:	8b 86 a4 03 00 00    	mov    eax,DWORD PTR [esi+0x3a4]
  49f312:	66 bb f0 ff          	mov    bx,0xfff0
  49f316:	e8 5d 3e f6 ff       	call   0x403178
  49f31b:	84 c0                	test   al,al
  49f31d:	74 06                	je     0x49f325
  49f31f:	c6 45 00 01          	mov    BYTE PTR [ebp+0x0],0x1
  49f323:	eb 6a                	jmp    0x49f38f
  49f325:	8b d7                	mov    edx,edi
  49f327:	8b 86 a8 03 00 00    	mov    eax,DWORD PTR [esi+0x3a8]
  49f32d:	66 bb f0 ff          	mov    bx,0xfff0
  49f331:	e8 42 3e f6 ff       	call   0x403178
  49f336:	84 c0                	test   al,al
  49f338:	74 06                	je     0x49f340
  49f33a:	c6 45 00 01          	mov    BYTE PTR [ebp+0x0],0x1
  49f33e:	eb 4f                	jmp    0x49f38f
  49f340:	8b d7                	mov    edx,edi
  49f342:	8b 86 ac 03 00 00    	mov    eax,DWORD PTR [esi+0x3ac]
  49f348:	66 bb f0 ff          	mov    bx,0xfff0
  49f34c:	e8 27 3e f6 ff       	call   0x403178
  49f351:	84 c0                	test   al,al
  49f353:	74 06                	je     0x49f35b
  49f355:	c6 45 00 01          	mov    BYTE PTR [ebp+0x0],0x1
  49f359:	eb 34                	jmp    0x49f38f
  49f35b:	8b d7                	mov    edx,edi
  49f35d:	8b 86 b4 03 00 00    	mov    eax,DWORD PTR [esi+0x3b4]
  49f363:	66 bb f0 ff          	mov    bx,0xfff0
  49f367:	e8 0c 3e f6 ff       	call   0x403178
  49f36c:	84 c0                	test   al,al
  49f36e:	74 06                	je     0x49f376
  49f370:	c6 45 00 01          	mov    BYTE PTR [ebp+0x0],0x1
  49f374:	eb 19                	jmp    0x49f38f
  49f376:	8b d7                	mov    edx,edi
  49f378:	8b 86 b0 03 00 00    	mov    eax,DWORD PTR [esi+0x3b0]
  49f37e:	66 bb f0 ff          	mov    bx,0xfff0
  49f382:	e8 f1 3d f6 ff       	call   0x403178
  49f387:	84 c0                	test   al,al
  49f389:	74 04                	je     0x49f38f
  49f38b:	c6 45 00 01          	mov    BYTE PTR [ebp+0x0],0x1
  49f38f:	5d                   	pop    ebp
  49f390:	5f                   	pop    edi
  49f391:	5e                   	pop    esi
  49f392:	5b                   	pop    ebx
  49f393:	c3                   	ret

; ---------------------------------------------------------------------
; Handler: DrawingMouseDown (0x0049a590 - 0x0049a800)
; ---------------------------------------------------------------------
  49a590:	55                   	push   ebp
  49a591:	8b ec                	mov    ebp,esp
  49a593:	83 c4 dc             	add    esp,0xffffffdc
  49a596:	53                   	push   ebx
  49a597:	56                   	push   esi
  49a598:	57                   	push   edi
  49a599:	33 db                	xor    ebx,ebx
  49a59b:	89 5d dc             	mov    DWORD PTR [ebp-0x24],ebx
  49a59e:	89 5d e0             	mov    DWORD PTR [ebp-0x20],ebx
  49a5a1:	89 5d e4             	mov    DWORD PTR [ebp-0x1c],ebx
  49a5a4:	88 4d ff             	mov    BYTE PTR [ebp-0x1],cl
  49a5a7:	8b f0                	mov    esi,eax
  49a5a9:	8b 7d 0c             	mov    edi,DWORD PTR [ebp+0xc]
  49a5ac:	33 c0                	xor    eax,eax
  49a5ae:	55                   	push   ebp
  49a5af:	68 a5 af 49 00       	push   0x49afa5
  49a5b4:	64 ff 30             	push   DWORD PTR fs:[eax]
  49a5b7:	64 89 20             	mov    DWORD PTR fs:[eax],esp
  49a5ba:	a0 b8 af 49 00       	mov    al,ds:0x49afb8
  49a5bf:	3a 45 10             	cmp    al,BYTE PTR [ebp+0x10]
  49a5c2:	0f 94 c3             	sete   bl
  49a5c5:	80 7d ff 01          	cmp    BYTE PTR [ebp-0x1],0x1
  49a5c9:	75 72                	jne    0x49a63d
  49a5cb:	8b 86 e4 05 00 00    	mov    eax,DWORD PTR [esi+0x5e4]
  49a5d1:	80 b8 9a 02 00 00 00 	cmp    BYTE PTR [eax+0x29a],0x0
  49a5d8:	74 63                	je     0x49a63d
  49a5da:	80 b8 98 02 00 00 00 	cmp    BYTE PTR [eax+0x298],0x0
  49a5e1:	74 5a                	je     0x49a63d
  49a5e3:	8b 86 e0 02 00 00    	mov    eax,DWORD PTR [esi+0x2e0]
  49a5e9:	c6 40 51 00          	mov    BYTE PTR [eax+0x51],0x0
  49a5ed:	b2 01                	mov    dl,0x1
  49a5ef:	a1 c8 1c 46 00       	mov    eax,ds:0x461cc8
  49a5f4:	e8 bb 77 fc ff       	call   0x461db4
  49a5f9:	89 45 f4             	mov    DWORD PTR [ebp-0xc],eax
  49a5fc:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]
  49a5ff:	50                   	push   eax
  49a600:	6a 01                	push   0x1
  49a602:	8b cf                	mov    ecx,edi
  49a604:	8b 55 f4             	mov    edx,DWORD PTR [ebp-0xc]
  49a607:	8b 86 e4 05 00 00    	mov    eax,DWORD PTR [esi+0x5e4]
  49a60d:	e8 de ac fe ff       	call   0x4852f0
  49a612:	8b 45 f4             	mov    eax,DWORD PTR [ebp-0xc]
  49a615:	e8 ee 7a fc ff       	call   0x462108
  49a61a:	8b d0                	mov    edx,eax
  49a61c:	8b 86 e4 05 00 00    	mov    eax,DWORD PTR [esi+0x5e4]
  49a622:	e8 35 ae fe ff       	call   0x48545c
  49a627:	b2 01                	mov    dl,0x1
  49a629:	8b 86 44 05 00 00    	mov    eax,DWORD PTR [esi+0x544]
  49a62f:	e8 2c dc fd ff       	call   0x478260
  49a634:	8b d6                	mov    edx,esi
  49a636:	8b c6                	mov    eax,esi
  49a638:	e8 93 37 00 00       	call   0x49ddd0
  49a63d:	8b 86 d0 04 00 00    	mov    eax,DWORD PTR [esi+0x4d0]
  49a643:	80 b8 2a 01 00 00 00 	cmp    BYTE PTR [eax+0x12a],0x0
  49a64a:	74 3a                	je     0x49a686
  49a64c:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]
  49a64f:	50                   	push   eax
  49a650:	53                   	push   ebx
  49a651:	b2 01                	mov    dl,0x1
  49a653:	a1 b0 9f 45 00       	mov    eax,ds:0x459fb0
  49a658:	e8 b3 0f fc ff       	call   0x45b610
  49a65d:	8b d0                	mov    edx,eax
  49a65f:	8b cf                	mov    ecx,edi
  49a661:	8b 86 e4 05 00 00    	mov    eax,DWORD PTR [esi+0x5e4]
  49a667:	e8 84 ac fe ff       	call   0x4852f0
  49a66c:	84 db                	test   bl,bl
  49a66e:	75 16                	jne    0x49a686
  49a670:	b2 01                	mov    dl,0x1
  49a672:	8b 86 44 05 00 00    	mov    eax,DWORD PTR [esi+0x544]
  49a678:	e8 e3 db fd ff       	call   0x478260
  49a67d:	8b d6                	mov    edx,esi
  49a67f:	8b c6                	mov    eax,esi
  49a681:	e8 4a 37 00 00       	call   0x49ddd0
  49a686:	8b 86 d4 04 00 00    	mov    eax,DWORD PTR [esi+0x4d4]
  49a68c:	80 b8 2a 01 00 00 00 	cmp    BYTE PTR [eax+0x12a],0x0
  49a693:	74 3a                	je     0x49a6cf
  49a695:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]
  49a698:	50                   	push   eax
  49a699:	53                   	push   ebx
  49a69a:	b2 01                	mov    dl,0x1
  49a69c:	a1 88 a1 45 00       	mov    eax,ds:0x45a188
  49a6a1:	e8 4a 13 fc ff       	call   0x45b9f0
  49a6a6:	8b d0                	mov    edx,eax
  49a6a8:	8b cf                	mov    ecx,edi
  49a6aa:	8b 86 e4 05 00 00    	mov    eax,DWORD PTR [esi+0x5e4]
  49a6b0:	e8 3b ac fe ff       	call   0x4852f0
  49a6b5:	84 db                	test   bl,bl
  49a6b7:	75 16                	jne    0x49a6cf
  49a6b9:	b2 01                	mov    dl,0x1
  49a6bb:	8b 86 44 05 00 00    	mov    eax,DWORD PTR [esi+0x544]
  49a6c1:	e8 9a db fd ff       	call   0x478260
  49a6c6:	8b d6                	mov    edx,esi
  49a6c8:	8b c6                	mov    eax,esi
  49a6ca:	e8 01 37 00 00       	call   0x49ddd0
  49a6cf:	8b 86 d8 04 00 00    	mov    eax,DWORD PTR [esi+0x4d8]
  49a6d5:	80 b8 2a 01 00 00 00 	cmp    BYTE PTR [eax+0x12a],0x0
  49a6dc:	74 3a                	je     0x49a718
  49a6de:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]
  49a6e1:	50                   	push   eax
  49a6e2:	53                   	push   ebx
  49a6e3:	b2 01                	mov    dl,0x1
  49a6e5:	a1 38 a5 45 00       	mov    eax,ds:0x45a538
  49a6ea:	e8 e9 1b fc ff       	call   0x45c2d8
  49a6ef:	8b d0                	mov    edx,eax
  49a6f1:	8b cf                	mov    ecx,edi
  49a6f3:	8b 86 e4 05 00 00    	mov    eax,DWORD PTR [esi+0x5e4]
  49a6f9:	e8 f2 ab fe ff       	call   0x4852f0
  49a6fe:	84 db                	test   bl,bl
  49a700:	75 16                	jne    0x49a718
  49a702:	b2 01                	mov    dl,0x1
  49a704:	8b 86 44 05 00 00    	mov    eax,DWORD PTR [esi+0x544]
  49a70a:	e8 51 db fd ff       	call   0x478260
  49a70f:	8b d6                	mov    edx,esi
  49a711:	8b c6                	mov    eax,esi
  49a713:	e8 b8 36 00 00       	call   0x49ddd0
  49a718:	8b 86 c0 04 00 00    	mov    eax,DWORD PTR [esi+0x4c0]
  49a71e:	80 b8 2a 01 00 00 00 	cmp    BYTE PTR [eax+0x12a],0x0
  49a725:	74 3a                	je     0x49a761
  49a727:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]
  49a72a:	50                   	push   eax
  49a72b:	53                   	push   ebx
  49a72c:	b2 01                	mov    dl,0x1
  49a72e:	a1 e4 a8 45 00       	mov    eax,ds:0x45a8e4
  49a733:	e8 74 24 fc ff       	call   0x45cbac
  49a738:	8b d0                	mov    edx,eax
  49a73a:	8b cf                	mov    ecx,edi
  49a73c:	8b 86 e4 05 00 00    	mov    eax,DWORD PTR [esi+0x5e4]
  49a742:	e8 a9 ab fe ff       	call   0x4852f0
  49a747:	84 db                	test   bl,bl
  49a749:	75 16                	jne    0x49a761
  49a74b:	b2 01                	mov    dl,0x1
  49a74d:	8b 86 44 05 00 00    	mov    eax,DWORD PTR [esi+0x544]
  49a753:	e8 08 db fd ff       	call   0x478260
  49a758:	8b d6                	mov    edx,esi
  49a75a:	8b c6                	mov    eax,esi
  49a75c:	e8 6f 36 00 00       	call   0x49ddd0
  49a761:	8b 86 c4 04 00 00    	mov    eax,DWORD PTR [esi+0x4c4]
  49a767:	80 b8 2a 01 00 00 00 	cmp    BYTE PTR [eax+0x12a],0x0
  49a76e:	74 3a                	je     0x49a7aa
  49a770:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]
  49a773:	50                   	push   eax
  49a774:	53                   	push   ebx
  49a775:	b2 01                	mov    dl,0x1
  49a777:	a1 94 ac 45 00       	mov    eax,ds:0x45ac94
  49a77c:	e8 37 2d fc ff       	call   0x45d4b8
  49a781:	8b d0                	mov    edx,eax
  49a783:	8b cf                	mov    ecx,edi
  49a785:	8b 86 e4 05 00 00    	mov    eax,DWORD PTR [esi+0x5e4]
  49a78b:	e8 60 ab fe ff       	call   0x4852f0
  49a790:	84 db                	test   bl,bl
  49a792:	75 16                	jne    0x49a7aa
  49a794:	b2 01                	mov    dl,0x1
  49a796:	8b 86 44 05 00 00    	mov    eax,DWORD PTR [esi+0x544]
  49a79c:	e8 bf da fd ff       	call   0x478260
  49a7a1:	8b d6                	mov    edx,esi
  49a7a3:	8b c6                	mov    eax,esi
  49a7a5:	e8 26 36 00 00       	call   0x49ddd0
  49a7aa:	8b 86 c8 04 00 00    	mov    eax,DWORD PTR [esi+0x4c8]
  49a7b0:	80 b8 2a 01 00 00 00 	cmp    BYTE PTR [eax+0x12a],0x0
  49a7b7:	74 3a                	je     0x49a7f3
  49a7b9:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]
  49a7bc:	50                   	push   eax
  49a7bd:	53                   	push   ebx
  49a7be:	b2 01                	mov    dl,0x1
  49a7c0:	a1 44 b0 45 00       	mov    eax,ds:0x45b044
  49a7c5:	e8 be 35 fc ff       	call   0x45dd88
  49a7ca:	8b d0                	mov    edx,eax
  49a7cc:	8b cf                	mov    ecx,edi
  49a7ce:	8b 86 e4 05 00 00    	mov    eax,DWORD PTR [esi+0x5e4]
  49a7d4:	e8 17 ab fe ff       	call   0x4852f0
  49a7d9:	84 db                	test   bl,bl
  49a7db:	75 16                	jne    0x49a7f3
  49a7dd:	b2 01                	mov    dl,0x1
  49a7df:	8b 86 44 05 00 00    	mov    eax,DWORD PTR [esi+0x544]
  49a7e5:	e8 76 da fd ff       	call   0x478260
  49a7ea:	8b d6                	mov    edx,esi
  49a7ec:	8b c6                	mov    eax,esi
  49a7ee:	e8 dd 35 00 00       	call   0x49ddd0
  49a7f3:	8b 86 cc 04 00 00    	mov    eax,DWORD PTR [esi+0x4cc]
  49a7f9:	80 b8 2a 01 00 00 00 	cmp    BYTE PTR [eax+0x12a],0x0

; ---------------------------------------------------------------------
; Handler: DrawingOnWireSelected (0x0049b7d4 - 0x0049b7e0)
; ---------------------------------------------------------------------
  49b7d4:	55                   	push   ebp
  49b7d5:	8b ec                	mov    ebp,esp
  49b7d7:	84 c9                	test   cl,cl
  49b7d9:	5d                   	pop    ebp
  49b7da:	c2 0c 00             	ret    0xc
  49b7dd:	8d 40 00             	lea    eax,[eax+0x0]

; ---------------------------------------------------------------------
; Handler: DrawingOnPinSelected (0x0049b7cc - 0x0049b7d4)
; ---------------------------------------------------------------------
  49b7cc:	55                   	push   ebp
  49b7cd:	8b ec                	mov    ebp,esp
  49b7cf:	5d                   	pop    ebp
  49b7d0:	c2 0c 00             	ret    0xc
  49b7d3:	90                   	nop

